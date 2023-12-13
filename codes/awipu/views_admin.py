import time

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dappx.models import UserMonitor, UserProfileInfo, OrganizationMember
from dappx.models import GpsCheckin, VideoUpload
from dappx.models import OrganizationMemberMonitor
from common import config
import urllib.parse
from itertools import chain
import operator

logger = config.get_logger()


def user_profile_dict(user_profile):
    return {
        'name': user_profile.name,
        'email': user_profile.user.email,
        'days_sober': user_profile.days_sober,
        'sober_date': user_profile.sober_date,
        'created_at': time.mktime(user_profile.created_at.timetuple())
    }


def monitor_feedback_dict(feedback):
    return {
        'name': feedback.user.name,
        'email': feedback.user.email,
        'message': feedback.message,
        'created_at': time.mktime(feedback.created_at.timetuple())
    }


def get_user_events(user):
    video_events = VideoUpload.objects.filter(user=user).all()
    gps_events = GpsCheckin.objects.filter(user=user).all()

    events = []
    for event in gps_events:
        t = event.created_at
        events.append({
            'id': event.id,
            'type': 'gps',
            'lat': event.lat,
            'lng': event.lng,
            'msg': event.msg,
            # 'monitor_feedbacks': [monitor_feedback_dict(f)
            #                     for f in event.monitor_feedback],
            'created_at': time.mktime(t.timetuple())})

    for event in video_events:
        t = event.created_at
        events.append({
            'id': event.video_id(),
            'type': 'video',
            'url': event.video_api_link(),
            # 'monitor_feedbacks': [monitor_feedback_dict(f)
            #                     for f in event.monitor_feedback],
            'created_at': time.mktime(t.timetuple())})

    events = sorted(events, key=lambda i: i['created_at'], reverse=True)

    result = user_profile_dict(
        UserProfileInfo.objects.filter(user=user).first()
    )
    result['events'] = events

    return result


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patients(request):
    # find users who have set this user as a monitor
    patients = UserMonitor.objects.filter(
        notify_email=request.user.email).all()

    patients_info = [
        get_user_events(patient.user)
        for patient in patients
    ]

    return Response({
        'patients': patients_info
    }, 201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patient_events(request):
    # find users who have set this user as a monitor

    filter_type = request.GET.get("filter_type")
    patient = urllib.parse.unquote(request.GET.get("email", ""))
    users = []
    profiles_map = {}

    # get all patients
    if not patient:
        patients = UserMonitor.objects.filter(
            notify_email=request.user.email
        ).all()

        for patient in patients:
            # XXX hassan make query in bulk
            profile = UserProfileInfo.objects.filter(
                user=patient.user
            ).first()
            profiles_map[patient.user.email] = profile
            users.append(patient.user)

    else:
        user = User.objects.filter(username=patient).first()
        profile = UserProfileInfo.objects.filter(user=user).first()
        profiles_map[user.email] = profile
        allowed = UserMonitor.objects.filter(
            notify_email=request.user.email, user=user).first()

        if not allowed:
            return Response({
                'status': "%s not viewable by %s" % (patient,
                                                     request.user.email)
            })

        users.append(user)

    print("len %s" % len(users))
    video_events = []
    gps_events = []
    # XXX hassan figure out to do in bulk
    for user in users:
        video_events += VideoUpload.objects.filter(user=user).all()
        gps_events += GpsCheckin.objects.filter(user=user).all()


    events = []
    if filter_type == 'gps' or not filter_type:
        for event in gps_events:
            t = event.created_at
            events.append({
                'id': event.id,
                'type': 'gps',
                'lat': event.lat,
                'lng': event.lng,
                'msg': event.msg,
                'name': profiles_map[event.user.email].name,
                'email': event.user.email,
                'created_at': time.mktime(t.timetuple())})

    if filter_type == 'video' or not filter_type:
        for event in video_events:
            t = event.created_at
            events.append({
                'id': event.id,
                'type': 'video',
                'email': event.user.email,
                'name': profiles_map[event.user.email].name,
                'url': event.video_api_link(),
                'created_at': time.mktime(t.timetuple())})

    events = sorted(events, key=lambda i: i['created_at'], reverse=True)

    paginator = PageNumberPagination()
    paginator.page_size = 50

    page = paginator.paginate_queryset(events, request)
    if page is not None:
        return paginator.get_paginated_response(page)

    return Response(events)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_last_patient_event(request):
    user_id = request.GET.get("user_id")
    print(user_id)
    user = User.objects.filter(id=int(user_id)).first()
    print(user.email)

    allowed_members = OrganizationMemberMonitor.objects.filter(
        client=user)
    print(allowed_members)
    for allowed_member in allowed_members:
        if allowed_member.user.email == request.user.email:
            allowed = True
            break
    else:
        allowed = UserMonitor.objects.filter(
            notify_email=request.user.email).first()

    if not allowed:
        return Response({
            'status': "%s not viewable by %s" % (user_id,
                                                 request.user.email)
        })

    profile = UserProfileInfo.objects.filter(user=user).first()
    video_event = VideoUpload.objects.filter(
        user=user
    ).order_by('-created_at').first()
    gps_event = GpsCheckin.objects.filter(
        user=user
    ).order_by('-created_at').first()

    if video_event and gps_event:
        if video_event.created_at > gps_event.created_at:
            return Response({
                'id': video_event.video_id(),
                'user': profile.user_hash,
            })
        else:
            return Response({
                'id': gps_event.id,
                'user': profile.user_hash,
            })

    if not video_event and gps_event:
        return Response({
            'id': gps_event.id,
            'user': profile.user_hash,
        })

    if video_event and not gps_event:
        return Response({
            'id': video_event.video_id(),
            'user': profile.user_hash,
        })
    return Response('no_events')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_patient_events_v2(request):
    # find users who have set this user as a monitor
    start = time.time()
    filter_type = request.GET.get("filter_type")
    patient = urllib.parse.unquote(request.GET.get("email", ''))
    users = []
    profiles_map = {}

    # get all patients
    if not patient:
        patients = UserMonitor.objects.filter(
            notify_email=request.user.email).all()

        for patient in patients:
            profile = UserProfileInfo.objects.filter(
                user=patient.user).first()
            profiles_map[patient.user.email] = profile
            users.append(patient.user)

        member_org = OrganizationMember.objects.filter(
            user=request.user).first()
        users = User.objects.filter(userprofileinfo__user_org=member_org.organization).all()

    else:
        user = User.objects.filter(username=patient).first()
        profile = UserProfileInfo.objects.filter(user=user).first()
        profiles_map[user.email] = profile

        allowed_members = OrganizationMemberMonitor.objects.filter(
            client=user)
        for allowed_member in allowed_members:
            if allowed_member.user.email == request.user.email:
                allowed = True
                break
        else:
            allowed = UserMonitor.objects.filter(
                notify_email=request.user.email, user=user).first()

        if not allowed:
            return Response({
                'status': "%s not viewable by %s" % (patient,
                                                     request.user.email)
            })

        users.append(user)

    if not filter_type:
        video_events = VideoUpload.objects.filter(user__in=users).all()
        gps_events = GpsCheckin.objects.filter(user__in=users).all()
        events = chain(video_events, gps_events)
        events = sorted(events, key=operator.attrgetter('created_at'), reverse=True)
    elif filter_type == 'video':
        events = VideoUpload.objects.filter(user__in=users).oreder_by('created_at').all()
    elif filter_type == 'gps':
        events = GpsCheckin.objects.filter(user__in=users).oreder_by('created_at').all()
    else:
        events = []
    paginator = PageNumberPagination()
    paginator.page_size = 30
    paginate_queryset = paginator.paginate_queryset(events, request)
    data = []
    for obj in paginate_queryset:
        if isinstance(obj, GpsCheckin):
            t = obj.created_at
            data.append({
                'id': obj.id,
                'type': 'gps',
                'lat': obj.lat,
                'lng': obj.lng,
                'msg': obj.msg,
                # 'name': profiles_map[obj.user.email].name,
                'name': obj.user.userprofileinfo.name,
                'email': obj.user.email,
                'created_at': time.mktime(t.timetuple())
            })
        elif isinstance(obj, VideoUpload):
            t = obj.created_at
            data.append({
                'id': obj.video_id(),
                # "id": obj.video_id(),
                'type': 'video',
                'email': obj.user.email,
                'name': obj.user.userprofileinfo.name,
                # 'name': profiles_map[obj.user.email].name,
                'url': obj.video_api_link(),
                # 'url': obj.video_api_link(),
                'created_at': time.mktime(t.timetuple())
            })
    print(f"time to events serializer is {time.time() - start}")

    return Response(data)

