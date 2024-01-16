from utils.chirp import CHIRP

import arrow
from datetime import datetime
import json
from rest_framework.response import Response
from .models import Session, SessionPoint, Device, Dot
from math import sin, cos, sqrt, atan2, radians

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes

from rest_framework.permissions import IsAuthenticated
from django.core.serializers import serialize
from .serializer import *

from django.http import HttpResponse
# from push_notifications.models import GCMDevice
import requests
import json


@api_view(['POST'])
def set_profile_info(request):
    pass

def get_distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


@api_view(['GET'])
def devices(request):
    devices = Device.objects.filter().order_by("last_seen").values()

    for device in devices:
        device['last_seen_readable'] = arrow.get(
            device['last_seen']
        ).humanize()
    print(devices)
    return Response(devices)


@api_view(['GET', 'POST'])
def get_distances(request):
    # here we calculate on server side..
    dots = Dot.objects.filter()
    session_point = SessionPoint.objects.filter().last()
    print("session point...%s" % session_point)

    if not session_point:
        return Response({'dots': []})

    res = []
    for dot in dots:
        res.append({'id': dot.id,
                    'distance': get_distance(dot.latitude, dot.longitude,
                                             session_point.latitude,
                                             session_point.longitude)})

    print("Number of dots: %s" % len(dots))
    return Response({'dots': res})


speedFlow = ['normal','fast','tofast','slow','toslow']
from datetime import timedelta

def get_sp_distance(session_points):
    if not session_points:
        return {'distance_miles': 0,
                'distance_meters': 0,
                'interval_stats': []}

    interval_distance = 0
    interval_stats = []
    session_distance = 0
    start_session = None
    complete_one_mile = 0
    speed_per_mile_cover_last = 0
    for i in range(0, len(session_points) - 1):

        # assign it to first one at the start
        if start_session is None:
            start_session = session_points[i]

        distance = get_distance(
            session_points[i].latitude, session_points[i].longitude,
            session_points[i + 1].latitude, session_points[i + 1].longitude
        )

        if complete_one_mile == 0:
            speed_cover_per_mile = session_points[i].created_at

        session_distance += distance
        interval_distance += distance
        complete_one_mile += distance

        if (0.62137 * interval_distance >= 0.1):
            # Calculate time difference in seconds
            time_difference_seconds = (start_session.created_at - session_points[i].created_at).total_seconds()

            # Calculate speed in miles per hour
            mph = 0 if time_difference_seconds == 0 else (0.62137 * interval_distance) / (time_difference_seconds / 3600)

            start_session = session_points[i]
            interval_stats.append({
                'distance': interval_distance,
                'mph': mph,
                'hours': time_difference_seconds / 3600,
                'speedFlow': 'none'
            })

            interval_distance = 0

        if (0.62137 * complete_one_mile >= 1):
            # Calculate time difference in seconds
            time_difference_seconds = (speed_cover_per_mile - session_points[i].created_at).total_seconds()

            # Calculate speed in miles per hour
            mph = 0 if time_difference_seconds == 0 else (0.62137 * complete_one_mile) / (time_difference_seconds / 3600)

            if speed_per_mile_cover_last == 0:
                speed_type = speedFlow[0]
            elif speed_per_mile_cover_last > mph:
                speed_type = speedFlow[1]
            elif speed_per_mile_cover_last < mph:
                speed_type = speedFlow[3]

            speed_per_mile_cover_last = mph

            interval_stats.append({
                'distance': interval_distance,
                'mph': mph,
                'hours': time_difference_seconds / 3600,
                'speedFlow': speed_type
            })
            complete_one_mile = 0

    return {'distance_miles': session_distance * 0.62137,
            'distance_meters': session_distance * 1000,
            'interval_stats': interval_stats}

def get_miles_points(session_points):
    miles = 1
    if not session_points:
        return {'miles' : 0, 'time_taken': '0:00:00'}
    session_response = []

    start_lat = session_points[0].latitude
    start_long = session_points[0].longitude
    session_start_time = session_points[0].created_at

    for i in range(0, len(session_points) - 1):
        session_distance_per_km = get_distance(
            start_lat, start_long,
            session_points[i + 1].latitude, session_points[i +1].longitude
        )
        session_distance_per_mile = session_distance_per_km*0.62137
        if session_distance_per_mile >= 1:
            time_taken = session_points[i + 1].created_at - session_start_time
            seconds = time_taken.total_seconds()
            h = seconds//3600
            m = seconds//60
            seconds %= 60
            time_taken = "%d:%02d:%02d" % (h,m,seconds)
            session_response.append({
                'miles' : f"{miles-1}-{miles}",
                'time_taken' : time_taken })
            start_lat, start_long = session_points[i + 1].latitude, session_points[i +1].longitude
            session_start_time =  session_points[i + 1].created_at
            miles += 1
    return session_response

@api_view(['GET'])
def get_session_stats(request):

    total_session_points = SessionPoint.objects.filter().count()

    device = Device.objects.filter(
        key=request.GET.get("device_id")
    ).first()

    session = Session.objects.filter(
        device=device
    ).order_by("-id").first()

    session_points = SessionPoint.objects.filter(
        session=session
    ).order_by("-id")

    print(session_points)

    calcs = get_sp_distance(session_points)
    print(calcs)

    return Response({
        "interval_stats": calcs['interval_stats'],
        'miles': calcs['distance_miles'],
        'meters': calcs['distance_meters'],
        "session_id": session.id,
        "points_count": len(session_points),
        "session_time": session.started_at,
        "session_time": session.started_at,
        "session_time": session.started_at,
    })


@api_view(['GET'])
def sessions(request):
    return Response(Session.objects.filter().values())


@api_view(['GET'])
def session_points(request, session_id):
    return Response(SessionPoint.objects.filter(
        session__id=session_id
    ).values())


@api_view(['POST'])
def start(request):
    session = Session.objects.create()
    session.save()

    # if device does not exist when session is started
    # it is created here
    print(request.data)
    device_id = request.data.get("device_id")
    print(device_id)
    print(type(device_id))

    device = Device.objects.filter(key=device_id).first()
    if not device:
        device = Device()
        device.key = device_id


    device.last_seen = datetime.now()
    device.save()
    session.device = device
    session.save()

    return Response({'status': 'okay',
                     'session_id': session.id})


@api_view(['POST'])
def session_point(request):

    # XXX optimize this lookup.
    # print(request.data.get("session_id"))
    session = Session.objects.get(id=request.data.get("session_id"))
    # print("found session %s" % session)
    device = Device.objects.filter(
       key=request.data.get("device_id"))[0]

    session_point = SessionPoint()
    session_point.session = session
    session_point.device = device

    session_point.latitude = request.data.get("latitude")
    session_point.longitude = request.data.get("longitude")
    session_point.save()


    print("creating session_point %s" % session_point.id)

    return Response({'status': 'okay'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop(request):
    session_create = Session.objects.filter().last()
    session_create.ended_at = datetime.now()
    session_create.save()
    return Response({'status': 'k'})


@api_view(['POST'])
def bulk_sync_motions(request):
    device_id = request.data.get("device_id")
    source = request.data.get("source")
    motions_points = request.data.get("motions_points")
    print("motions_points:", motions_points)

    motions_points = json.loads(motions_points)

    for mp in motions_points:
        print("source:", source)
        print("device_id:", device_id)
        print("motions_point:", mp)

        device = Device.objects.filter(key=device_id).first()
        if not device:
            device = Device()
            device.key = device_id
            device.save()

        gxyz_point = GXYZPoint(
            g=int(mp['g']), x=int(mp['x']), y=int(mp['y']), z=int(mp['z']),
            device=device
        )
        gxyz_point.save()
        print("done!!\n")
    return Response({'status': 'k'},  safe=False)

@api_view(['POST'])
def gsm_Add(request):
    user = User.objects.get(id= request.data['user'])
    fcm_registration_id = request.data['fcm_registration_id']
    GCMDevice.objects.get_or_create(
        registration_id=fcm_registration_id,
        cloud_message_type="FCM", user=user)

    return Response({'status': 'okay'})

def send_notification(registration_ids , message_title , message_desc):
    fcm_api = "AAAA4UE3yG0:APA91bHFb0FoLZ_oH334w2Ho5mirUlELbhHHpU16KrjIwfl4_fK-bbHcOXTSk5jw9YWIZ1ZC1u_VNaXJ54xFNHVvN4Q507ew2xQFInRMsvYCdqx8eIwO6LNIFkCcBg-k0hQbbxEYtIJx"
    url = "https://fcm.googleapis.com/fcm/send"

    headers = {
    "Content-Type":"application/json",
    "Authorization": 'key='+fcm_api}

    payload = {
        "registration_ids" :registration_ids,
        "priority" : "high",
        "notification" : {
            "body" : message_desc,
            "title" : message_title,
            "image" : "https://i.ytimg.com/vi/m5WUPHRgdOA/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLDwz-yjKEdwxvKjwMANGk5BedCOXQ",
            "icon": "https://yt3.ggpht.com/ytc/AKedOLSMvoy4DeAVkMSAuiuaBdIGKC7a5Ib75bKzKO3jHg=s900-c-k-c0x00ffffff-no-rj",
        }
    }

    result = requests.post(url,  data=json.dumps(payload), headers=headers)
    print(result.json())

@api_view(['POST'])
def gsm_send(request):
    username = "TestUser"
    body = f"{username} is Leading this week..."
    title = "New Lead..."
    fcm_devices = GCMDevice.objects.filter(user = 1).distinct("registration_id")
    resp = fcm_devices.send_message(body, badge=1, sound="default",
                                    extra={"title": title,"icon": "icon",
                                           "data": "data",
                                           "image": "image"})
    print(f"Share Moment FCM: {resp}")

    # print(dir(fcm_devices))
    # send_notification(resgistration , 'testingg' , 'testing')
    return Response("sent")
