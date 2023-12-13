from django.contrib.auth.models import User
from django.contrib.sites.models import Site

import requests
import json

from .models import UserMonitor, OrganizationMemberMonitor
from .models import UserProfileInfo, OrganizationMember
from . import email_utils
from . import constants
from common import config


logger = config.get_logger()


def get_user_monitors(request):
    user = User.objects.filter(username=request.user.email).first()
    users = UserMonitor.objects.filter(user=user).all()

    notify_group = [u.notify_email for u in users]

    # check notify_all setting
    user_profile = UserProfileInfo.objects.filter(user=user).first()
    if user_profile.user_org and user_profile.user_org.notify_all:
        # notify all org members
        org_monitors = OrganizationMember.objects.filter(
            organization=user_profile.user_org)

    else:
        org_monitors = OrganizationMemberMonitor.objects.filter(
            client=user)

    print("ORG MONITORS")
    print(org_monitors)
    for org_monitor in org_monitors:
        if org_monitor.user.email not in notify_group:
            notify_group.append(org_monitor.user.email)
    print(notify_group)
    return notify_group


def get_user_profile(user):
    if not hasattr(user, 'email'):
        return False

    return UserProfileInfo.objects.filter(
        user__username=user.email
    ).first()


def notify_feedback(message, subject, send_to_email, send_from_email):
    email_utils.send_raw_email(
        send_to_email,  # send report here
        send_from_email,  # replies to goes here
        subject,
        message
    )


def notify_monitors_video(request, event):
    notify_users = get_user_monitors(request)
    profile = get_user_profile(request.user)

    msg = (
        "<p>I AM video from %s - "
        "<a href='https://m.useiam.com%s'>Click to play</a></p>" %
        (profile.name, event['video_model'].video_source_link())
    )

    logger.info("Sendering notify email to: %s" % notify_users)
    domain_name = Site.objects.last().domain

    for notify_user in notify_users:

        # Check if user is on platform
        if not UserProfileInfo.objects.filter(
            user__username=notify_user,
        ).count():
            send_msg = (
                "<p>You must created an account "
                "<a href='https://%s/signup.html?email=%s'>here</a> "
                "to view first.<p>" % ('m.useiam.com', notify_user)) + msg
        else:
            logger.info("ON PLATFORM: %s" % notify_user)
            send_msg = msg

        footer = (
            "<p><a href='https://medium.com/@useIAM/tips-on-being-an-iam-monitor-953086e01e2d'>Tips on Being an IAM Monitor</a></p><a href='https://m.useiam.com'>Try I AM</a>"
        )

        email_utils.send_raw_email(
            notify_user,  # send report here
            request.user.email,  # replies to goes here
            'Video Checkin from %s' % profile.name,
            send_msg + footer
        )

    logger.info(msg)

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
    data = (
        str("VideoUpload: %s - https://%s%s" % (
            request.user.email,
            domain_name,
            event['uploaded_file_url'])
            ))
    body = {"text": "%s" % data, 'username': 'pam-server'}
    requests.put(url, data=json.dumps(body))


def notify_gps_checkin(gps_checkin, request):

    lat = gps_checkin.lat
    lng = gps_checkin.lng
    msg = gps_checkin.msg

    lat_long_url = 'https://www.google.com/maps/place/%s,%s' % (lat, lng)
    msg += "\n\n\n%s" % lat_long_url

    profile = get_user_profile(request.user)

    gps_link = '/review-video.html?id=%s&user=%s' % (
        gps_checkin.id, gps_checkin.user)
    msg = (
        "<p>I AM GPS Checkin from %s - "
        "<a href='https://m.useiam.com%s'>View Checkin</a></p>" %
        (profile.name, gps_link)
    )

    notify_users = get_user_monitors(request)
    for notify_user in notify_users:
        if not notify_user:
            logger.info("sending email to [%s]" % notify_user)
            continue

        logger.info("sending email to %s" % notify_user)
        email_utils.send_raw_email(
            notify_user,  # send report here
            request.user.email,  # replies to goes here
            'GPS Checkin from %s' % profile.name,
            msg)

    # auto email the user a copy
    email_utils.send_raw_email(
        request.user.email,  # send report here
        request.user.email,  # replies to goes here
        'GPS useIAM Checkin',
        msg)

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
    data = "GspCheckin: %s - %s (%s, %s)" % (request.user.email,
                                             msg, lat, lng)
    body = {"text": "%s" % data, 'username': 'pam-server'}
    requests.put(url, data=json.dumps(body))


def notify_monitor_email(request, notify_email, monitor_user):

    logger.info("invite source: %s" % request.data.get("source"))
    signup_link = (
        "\n\nhttps://%s/signup.html?email=%s"
        % (request.data.get("source"), request.data.get('notify_email')))
    profile = get_user_profile(request.user)

    if monitor_user:
        logger.info("monitor user already exists")
        message = constants.existing_monitor_message
    else:
        logger.info("monitor user does not exist")
        message = constants.existing_monitor_message + signup_link

    email_utils.send_raw_email(
        to_email=request.data.get("notify_email"),
        reply_to=request.user.username,
        subject='useIAM: %s added you as a monitor'
                % profile.name,
        message_text=message)


def notify_monitor(request, notify_email):
    # check to see if notify_email has account

    logger.info("user: %s added notify_email: %s" %
                (request.user.username, notify_email))
    monitor_user = User.objects.filter(
        username=notify_email
    ).first()

    notify_monitor_email(request, notify_email, monitor_user)
