import random
import time
from os.path import dirname, join
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.serializers import (
    UserSerializer, UserProfileSerializer, GpsCheckinSerializer,
    VideoUploadSerializer
)
from dappx.models import UserProfileInfo, GpsCheckin, VideoUpload
from dappx.models import UserMonitor, SubscriptionEvent
from dappx.models import OrganizationMember, OrganizationMemberMonitor
from dappx.models import MonitorFeedback, Organization
from dappx.views import _create_user
from dappx import email_utils
from dappx.views import convert_and_save_video, stream_video
from dappx.notify_utils import notify_gps_checkin, notify_monitor
from dappx.notify_utils import notify_feedback
from dappx import constants
from dappx import utils
from common import config

from magic_link.models import MagicLink
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django.http import Http404
from django.conf import settings

logger = config.get_logger()

user = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    http_method_names = ['post']


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserProfileInfo.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer

    def list(self, request):
        profile = UserProfileInfo.objects.filter(
            id=request.user.id
        ).first()
        return Response({
            'days_sober': utils.calc_days_sober(profile),
            'sober_date': profile.sober_date,
            'notify_email': profile.notify_email
        })


class GpsCheckinViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = GpsCheckin.objects.all().order_by('-id')
    serializer_class = GpsCheckinSerializer

    def perform_create(self, serializer):
        logger.error("Creating gps event for user %s" % self.request.user)
        gps_checkin = serializer.save(user=self.request.user)
        notify_gps_checkin(
            gps_checkin, self.request
        )
        print("Created...")


class VideoUploadViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = VideoUpload.objects.all().order_by('-id')
    serializer_class = VideoUploadSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def video_upload(request):
    logger.error("I am here video_upload")
    logger.error(request.FILES)
    logger.error(request.data)
    video = request.data.get('video')
    if not video:
        logger.error("no video file found")
        return Response({'message': 'video is required'}, 400)

    video = convert_and_save_video(video, request)
    return Response({'videoUrl': video.videoUrl})


def passthrough_domain(source):
    pass


def is_passthrough_domain(source):
    passthrough_domains = [
        # 'cardoneaccountability.com',
    ]
    if source in passthrough_domains:
        return True
    return False


@api_view(['POST'])
def create_user(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email'):
        return Response({
            'message': 'Missing parameters. Email is required'
        })

    if not data.get('days_sober'):
        data['days_sober'] = '0'

    data['email'] = data['email'].lower()
    user = User.objects.filter(username=data['email']).first()

    logger.info("Create user %s" % data)

    if user:
        email_user_login_code(user, data)
        return Response({'message': 'User already exists'})

    _create_user(**data)
    user = User.objects.filter(username=data['email']).first()

    # some interesting logic exists here. If domain is passthrough
    # we auto login user to account using trust model only for new accounts.
    # if not is_passthrough_domain(data.get("source")):
    #     email_user_login_code(user, data)
    # else:
    token = Token.objects.get_or_create(user=user)
    data['token'] = token[0].key

    data.pop('password')
    data['message'] = "User created"

    return Response(data)


@api_view(['POST'])
def login_user_code(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email') or not data.get('code'):
        return Response({
            'message': 'Missing parameters. Email and Code is required'
        }, 407)

    data['email'] = data['email'].lower()
    print(data)
    user = User.objects.filter(username=data['email']).first()
    user_profile = UserProfileInfo.objects.filter(user=user).first()
    print(user_profile)
    print(request)
    logger.info("Verify code: %s" % data)
    if (data['code'] and user_profile.login_code and
            user_profile.login_code == data['code']):
        token = Token.objects.get_or_create(user=user)
        logger.info("Code verify success")
        # clear the login_code!
        user_profile.login_code = None

        # check set hostname org
        org = Organization.objects.filter(
            hostname=data['source'].lower()).first()
        if org:
            user_profile.user_org = org
        user_profile.save()
        data['token'] = token[0].key

        return Response(data)

    logger.info("Error verify code success")
    return Response({'message': 'Error validating code'}, 407)


def email_user_login_code(user, data):
    return
    source = data.get("source")
    page = data.get("page", "")
    user_profile = UserProfileInfo.objects.filter(user=user).first()
    user_profile.login_code = random.randint(1000, 9999)
    user_profile.save()

    if 'index' in page or page is '':
        direct_link = (
            "https://%s?email=%s&code=%s" %
            (source, user.email, user_profile.login_code))
    else:
        direct_link = (
            "https://%s/review-video.html?email=%s&code=%s" %
            (source, user.email, user_profile.login_code))
        if data.get("id"):
            direct_link = direct_link + "&id=%s" % data.get("id")
        if data.get("user"):
            direct_link = direct_link + "&user=%s" % data.get("user")

    email_utils.send_email(
        to_email=user.email,
        subject='useIAM: Your Login Code',
        message="Click here to login: %s or enter code %s" %
        (direct_link, user_profile.login_code))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_organization_member(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email') or not data.get('password'):
        return Response({
            'message': 'Missing parameters. Email and password is required'
        })

    data['email'] = data['email'].lower()
    user = User.objects.filter(username=data['email']).first()

    if not user:
        _create_user(**data)

    user = User.objects.filter(username=data['email']).first()
    if user:
        org_member = OrganizationMember.objects.filter(user=user).first()
        if not org_member:
            org_member = OrganizationMember()
            org_member.user = user
            org_member.save()

        return Response({'message': 'User already exists'})

    data.pop('password')
    data['message'] = "User created"

    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_note(request):
    user_profile = UserProfileInfo.objects.filter(user=request.user).first()
    user_profile.notes = request.data.get('notes')
    user_profile.save()

    return Response({
        'response': 'okay',
    }, 201)



@api_view(['PUT', 'GET'])
@permission_classes([IsAuthenticated])
def add_monitor(request):
    user = User.objects.filter(username=request.user.email).first()
    notify_email = request.data.get('notify_email').lower()

    # check if notify_email is already set for user
    have = UserMonitor.objects.filter(user=user,
                                      notify_email=notify_email).first()
    if have:
        return Response({
            'msg': '%s is already a monitor user for you',
        }, 201)

    user_monitor = UserMonitor()
    user_monitor.user = user
    user_monitor.notify_email = notify_email
    user_monitor.save()

    notify_monitor(request, notify_email)

    return Response({
        'response': 'okay',
    }, 201)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def remove_monitor(request):
    user = User.objects.filter(username=request.user.email).first()
    notify_email = request.data.get('notify_email')
    monitors = UserMonitor.objects.filter(user=user,
                                          notify_email=notify_email).all()
    if monitors:
        UserMonitor.objects.filter(user=user,
                                   notify_email=notify_email).delete()

    return Response({
        'status': 'okay',
    }, 201)


# XXX rename to get_event_info
@api_view(['GET'])
def get_video_info(request):
    token = Token.objects.get(key=request.GET.get("token"))

    logger.info("requesting video as user: %s" % token.user.email)
    resp_body = {}

    try:
        int(request.GET.get("id"))
        video = GpsCheckin.objects.filter(
            id=int(request.GET.get("id"))).first()
        resp_body['type'] = 'gps'
        resp_body['lat'] = video.lat
        resp_body['lng'] = video.lng
        resp_body['msg'] = video.msg
    except ValueError:
        resp_body['type'] = 'video'
        path = '/media/%s/%s' % (request.GET.get("user"),
                                 request.GET.get("id"))
        video = VideoUpload.objects.filter(videoUrl=path).first()
        resp_body['url'] = video.video_ref_link()

    if not video:
        return Response({
            'status': 'error',
        }, 201)

    profile = UserProfileInfo.objects.filter(
        user__username=video.user.email
    ).first()

    feedbacks = video.monitor_feedback.all()
    # get monitors of user
    user_monitors = UserMonitor.objects.filter(user=video.user).all()
    user_monitor_emails = [u.notify_email for u in user_monitors]

    video_feedback = []

    # here we only show feedback comments to owner of content otherwise if
    # request is from montior user we just show their feedbacks
    if token.user.email == video.user.email:
        video_feedback = [
            {'user': feedback.user.email, 'message': feedback.message,
             'created_at': time.mktime(feedback.created_at.timetuple())}
            for feedback in feedbacks]
    elif token.user.email in user_monitor_emails:
        for feedback in feedbacks:
            if feedback.user.email == token.user.email:
                video_feedback.append({'user': feedback.user.email,
                                       'message': feedback.message,
                                       'created_at': time.mktime(
                                            feedback.created_at.timetuple())
                                       })


    # include monitors from org
    org_monitors = OrganizationMemberMonitor.objects.filter(
        client=video.user)
    for org_monitor in org_monitors:
        if org_monitor.user.email not in user_monitor_emails:
            user_monitor_emails.append(org_monitor.user.email)

    logger.info("User %s monitors are %s"
                % (video.user.email, user_monitor_emails))

    resp_body.update({
        'owner_email': video.user.email,
        'feedback': video_feedback,
        'owner_name': profile.name,
        'created_at': time.mktime(video.created_at.timetuple()),
    })
    if token.user.email == video.user.email:
        resp_body['video_owner'] = True
        return Response(resp_body, 201)

    elif token.user.email in user_monitor_emails:
        resp_body['video_owner'] = False
        return Response(resp_body, 201)

    return Response({
        'status': 'error',
    }, 201)


@api_view(['POST'])
def send_feedback(request):
    token = Token.objects.get(key=request.GET.get("token"))
    user = User.objects.filter(username=token.user.email).first()

    try:
        int(request.GET.get("id"))
        # if we get here this is gps-checkin
        # test
        video = GpsCheckin.objects.filter(
            id=int(request.GET.get("id"))).first()
    except ValueError:
        path = '/media/%s/%s' % (request.GET.get("user"),
                                 request.GET.get("id"))
        video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        raise Http404

    # XXX todo add fitlering below to check monitor access to video objs

    logger.info("sending feedback as user: %s msg: %s"
                % (token.user.email, request.data.get("message")))

    monitor_feedback = MonitorFeedback.objects.create(
        user=user, message=request.data.get("message"))

    video.monitor_feedback.add(monitor_feedback)

    # email user who created the video the feedback

    profile = UserProfileInfo.objects.filter(
        user__username=token.user.email
    ).first()

    subject = "%s replied to your video submission" % profile.name
    notify_feedback(request.data.get("message"),
                    subject, video.user.email, token.user.email)

    return Response({'status': 'okay'})


@api_view(['GET'])
def review_video(request):
    token = Token.objects.get(key=request.GET.get("token"))
    logger.info("requesting video as user: %s" % token.user.email)
    path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
    video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        raise Http404

    if video and token.user.is_superuser:
        return stream_video(request, path)

    # get monitors of user
    user_monitors = UserMonitor.objects.filter(user=video.user).all()
    user_monitor_emails = [u.notify_email for u in user_monitors]

    org_monitors = OrganizationMemberMonitor.objects.filter(
        client=video.user)
    for org_monitor in org_monitors:
        if org_monitor.user.email not in user_monitor_emails:
            user_monitor_emails.append(org_monitor.user.email)

    logger.info("User %s monitors are %s"
                % (video.user.email, user_monitor_emails))

    if token.user.email in user_monitor_emails:
        logger.info("User %s is a monitor for %s"
                    % (token.user.email, video.user.email))
        return stream_video(request, path)

    elif token.user.email == video.user.email:
        logger.info("User is viewing their own video: %s:%s"
                    % (token.user.email, video.user.email))
        return stream_video(request, path)

    raise Http404


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_activity(request):
    user = User.objects.filter(username=request.user.email).first()
    video_events = VideoUpload.objects.filter(user=user).all()
    gps_events = GpsCheckin.objects.filter(user=user).all()
    events = []

    for event in gps_events:
        t = event.created_at
        events.append({
            'type': 'gps',
            'lat': event.lat,
            'lng': event.lng,
            'msg': event.msg,
            'created_at': time.mktime(t.timetuple())})

    for event in video_events:
        t = event.created_at
        events.append({
            'type': 'video',
            'url': event.video_ref_link(),
            'created_at': time.mktime(t.timetuple())})

    return Response({
        'events': sorted(events,
                         key=lambda i: i['created_at'], reverse=True)[0:20]
    })


@api_view(['PUT', 'GET'])
def profile(request):
    logger.info("get profile info %s %s"
                % (request.data.get("paying"), request.user.email))
    profile = UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()

    monitors = []

    active_monitor = False

    if request.method == 'PUT':
        if str(request.data.get("paying")).lower() in ['true', 'false']:
            paying = request.data.get("paying").lower()
            profile.iap_blurb = request.data.get("iap_blurb")
            if paying == 'true':
                profile.paying = True
            else:
                profile.paying = False

            user = User.objects.filter(username=request.user.email).first()
            logger.info("Creating subscription event: %s %s %s" %
                        (profile.paying, user,
                         request.data.get("iap_blurb")))
            # keep track of subscription events
            SubscriptionEvent(
                user=user, subscription_id=request.data.get("iap_blurb"),
                paying=profile.paying).save()

        if request.data.get('days_sober'):
            profile.days_sober = request.data.get('days_sober')

        if request.data.get('notify_email'):

            no_change = False
            if profile.notify_email == request.data.get('notify_email'):
                no_change = True

            profile.notify_email = request.data.get('notify_email')
            monitor_user = User.objects.filter(
                username=profile.notify_email
            ).first()

            if monitor_user and no_change is False:
                email_utils.send_raw_email(
                    to_email=request.data.get("notify_email"),
                    reply_to=request.user.email,
                    subject='useIAM: %s added you as a monitor'
                            % profile.name,
                    message=constants.existing_monitor_message)
            elif not monitor_user and no_change is False:
                url = "https://" + request.META['HTTP_HOST']
                url += "/create_notify_user/" + profile.user_hash
                mail_text = constants.new_monitor_message + url
                email_utils.send_raw_email(
                    to_email=request.data.get("notify_email"),
                    reply_to=request.user.email,
                    subject='useIAM: %s added you as a monitor'
                            % profile.name,
                    message=mail_text)

        profile.save()

    else:
        if profile.notify_email:
            monitor_user = User.objects.filter(
                username=profile.notify_email
            ).first()
            if monitor_user:
                active_monitor = True
        user = User.objects.filter(username=request.user.email).first()
        users = UserMonitor.objects.filter(user=user).all()
        monitors = [u.notify_email for u in users]
    # Check to see to see if monitor_user is on platform

    print(profile.user_org)
    if profile.user_org:
        org = {
            'name': profile.user_org.name,
            'logo': profile.user_org.logo,
        }
    else:
        org = {
        }

    ret = {
        'user_org': org,
        'days_sober': utils.calc_days_sober(profile),
        'sober_date': profile.sober_date,
        'notify_email': profile.notify_email,
        'notes': profile.notes,
        'active_monitor': active_monitor,
        'monitors': monitors,
        # 'paying': profile.paying,
        'paying': True,
        'iap_blurb': profile.iap_blurb,
        'stripe_subscription_id': profile.stripe_subscription_id,
    }

    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if org_member:
        ret['org_member'] = {'name': org_member.organization.name,
                             'logo': org_member.organization.logo}
    else:
        ret['org_member'] = {}
    print(ret)

    return Response(ret, 201)


@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response(
            'Email is required', status=status.HTTP_400_BAD_REQUEST
        )

    # agent = AgentWeb.objects.filter(user__email=email).first()
    # if not agent:
    #     return Response(
    #         'Email is invalid', status=status.HTTP_400_BAD_REQUEST
    #     )
    form = PasswordResetForm(data={'email': email})
    # first_name = ''
    # if (agent.agent_profile_connector and
    #         agent.agent_profile_connector.full_name):
    #     profile_connector = agent.agent_profile_connector
    #     first_name = profile_connector.full_name.split()[0]

    if form.is_valid():
        form.save(
            request=request,
            html_email_template_name='registration/password_reset_email.html',
            extra_email_context={
                'agent_name': '',
                'reset_url': settings.WEBSITE_URL + 'reset-password.html'
            }
        )
    else:
        return Response(
            'Email is invalid', status=status.HTTP_400_BAD_REQUEST
        )

    return Response({'status': True})


@api_view(['POST'])
def send_magic_link(request):
    email = request.data['email']
    mode = request.data['mode']
    name = email.strip().split('@')
    user = User.objects.filter(username=email).first()
    if not user:
        password = User.objects.make_random_password()
        print("password", password)
        data = {
            'username': email,
            'email': email,
            'notify_email': email,
            'password': password,
            'name': name[0],
            'phone': '',
            'days_sober': 0,
            'sober_date': 0,
            'source': None
        }
        _create_user(**data)
    if email is None:
        data = {
            'status': False,
            'error': 'Email is required'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, email=email)
    link = MagicLink.objects.create(user=user)
    if link:
        if mode == 'web':
            login_url = settings.WEBSITE_URL + '?token=' + str(link.token)
            email_utils.send_email(
                to_email=email,
                subject='useIAM: Magic Link to Login',
                message="please click on this link %s for login " % login_url
            )
            data = {
                'status': True,
                'token': link.token
            }
        else:
            login_url = "useiam://?token=" + str(link.token)
            email_utils.send_email(
                to_email=email,
                subject='useIAM: Magic Link to Login',
                message="please click on this link %s for login " % login_url
            )
            data = {
                'status': True,
                'token': link.token
            }
    else:
        data = {
            'status': False,
        }

    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def auth_magic_link(request):
    token = request.data['token']
    if token is None:
        data = {
            'status': False,
            'error': 'Token is required'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    link = get_object_or_404(MagicLink, token=token)
    link.validate()
    link.authorize(request.user)
    print("#############")
    print(link.user.id)
    user = User.objects.get(id=link.user.id)
    serialized = UserSerializer(user)
    # link.login(request)
    link.disable()

    token, _ = Token.objects.get_or_create(user=link.user)

    data = {
        'status': True,
        'auth_token': token.key,
        # 'user': serialized.data
    }

    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def view_org_logo(request, name):
    link = 'media/img/'+name
    project_root = dirname(dirname(__file__))
    output_path = join(project_root, link)
    image_data = open(output_path, "rb").read()
    return HttpResponse(image_data, content_type="image/png")
