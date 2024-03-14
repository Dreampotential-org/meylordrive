import datetime
import hashlib
import json
import logging
import mimetypes
import os
import requests
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.http import JsonResponse
from django.http.response import StreamingHttpResponse
# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from wsgiref.util import FileWrapper

from . import email_utils
from . import notify_utils
from . import video_utils
from . import constants
from .models import UserProfileInfo
from .models import VideoUpload
from .models import UserMonitor
from xppda.forms import UserForm, UserProfileInfoForm
from utils import superuser_only
from utils import custom_render as render
from common import config

logger = config.get_logger()


def register(request):
    return render(request, 'xppda/index.html')


@superuser_only
def video(request):
    path = '/media/%s/%s' % (request.GET.get("user"),
                             request.GET.get("id"))
    return stream_video(request, path)


@login_required
def video_monitor(request):
    logger.error("View video request from: %s" % request.user)
    path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
    video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        raise Http404

    if video and request.user.is_superuser:
        return stream_video(request, path)

    video_owner = UserProfileInfo.objects.filter(user=video.user).first()

    # get monitors of user
    user_monitors = UserMonitor.objects.filter(user=video.user).all()
    user_monitor_emails = [u.notify_email for u in user_monitors]
    logging.info("User %s monitors are %s"
                 % (video.user.email, user_monitor_emails))

    monitor_user = UserProfileInfo.objects.filter(
        user__email=video_owner.notify_email
    ).first()

    if monitor_user:
        logger.info("monitor user for video is: %s" % monitor_user)
    else:
        logger.info("no monitor user")

    if monitor_user and monitor_user.user.email != request.user.email:
        raise Http404

    return stream_video(request, path)


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def monitor(request):
    return render(request, 'xppda/monitor.html', {})


def record_video_screen(request):
    return render(request, 'xppda/record.html')


def days_sober(date_joined):
    date_joined = (str(date_joined).split(" "))[0].split("-")
    current = datetime.datetime.now()
    joined = datetime.datetime(int(date_joined[0]),
                               int(date_joined[1]),
                               int(date_joined[2]))
    return (current - joined).days


@csrf_exempt
def post_slack_errors(request):
    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BF6H2L0M6/RMuFLttV91aKvlUXydV2yJgv'
    data = (str(request.POST))
    data += '\nSite: %s' % request.META['HTTP_HOST']
    body = {"text": "%s" % data,
            'username': 'js-logger'}

    requests.put(url, data=json.dumps(body))

    return JsonResponse({'error': 'Some error'}, status=200)


def convert_file(uploaded_file_url):
    outfile = "%s.mp4" % uploaded_file_url.rsplit(".", 1)[0]
    command = (
        'avconv -i ./%s -codec copy ./%s' % (uploaded_file_url, outfile)
    )
    print(command)
    os.system(command)
    return outfile


def compress_file(uploaded_file_url):
    outfile = "%s_resized.mp4" % uploaded_file_url.rsplit(".", 1)[0]
    command = (
        'avconv -i ./%s -strict -2 ./%s' % (uploaded_file_url, outfile)
    )
    print(command)
    os.system(command)
    return outfile


def stream_video(request, path):
    path = settings.BASE_DIR + path
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = video_utils.range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(video_utils.RangeFileWrapper(
            open(path, 'rb'), offset=first_byte, length=length), status=206,
            content_type=content_type
        )
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte,
                                                    size)
    else:
        resp = StreamingHttpResponse(
            FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp


def convert_and_save_video(myfile, request):
    user = request.user
    fs = FileSystemStorage()
    user_hash = hashlib.sha1(
        user.email.encode('utf-8')
    ).hexdigest()

    uploaded_name = (
        "%s/%s-%s" % (user_hash, uuid.uuid4(), myfile.name)
    ).lower()

    filename = fs.save(uploaded_name, myfile)
    uploaded_file_url = fs.url(filename)

    if uploaded_name[-4:] == '.mov':
        # ffmpeg!
        uploaded_file_url = convert_file(uploaded_file_url)
    # XXX resize video for android need to implement async processing

    logger.info("Uploaded video file: %s" % uploaded_file_url)

    # now lets create the db entry
    user = User.objects.get(id=user.id)
    video = VideoUpload.objects.create(
        videoUrl=uploaded_file_url, user=user,
        source=request.data.get("source")
    )

    notify_utils.notify_monitors_video(request, {
        "event_type": "video",
        "video_model": video,
        "uploaded_file_url": uploaded_file_url,
        "video_link": video.video_monitor_link()})

    return video


def upload_org_logo(myfile, request):
    fs = FileSystemStorage()
    uid = uuid.uuid4()
    uploaded_name = (
        "%s/%s-%s" % ('img', uid, myfile.name)
    ).lower()

    filename = fs.save(uploaded_name, myfile)

    save_filename = (
        "%s-%s" % (uid, myfile.name)
    ).lower()

    return save_filename


@csrf_exempt
@login_required
def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        logger.info("Video upload: %s" % request.POST)

        myfile = request.FILES['file']
        convert_and_save_video(myfile, request)

        return JsonResponse({'error': 'Some error'}, status=200)


# @csrf_exempt
@login_required
def record_video(request):
    files = request.data.get("file")
    userId = request.data.get('userId')
    fs = FileSystemStorage()
    try:
        filename = fs.save(files.name, files)
        uploaded_file_url = fs.url(filename)
    except Exception:
        logger.exception("Error")
        return Response({'error': 'Error uploading file'},
                        status=HTTP_400_BAD_REQUEST)
    print(type(files))
    print(uploaded_file_url)

    user = User.objects.get(id=userId)
    try:
        VideoUpload.objects.create(videoUrl=uploaded_file_url,
                                   user=user)
    except Exception:
        logger.exception("Error")
        return Response({'error': 'Error uploading file'},
                        status=HTTP_400_BAD_REQUEST)

    return Response({
        'message', 'Success'
    }, status=HTTP_200_OK)


def _create_user(**data):
    data['email'] = data['email'].lower()
    data['username'] = data['email']
    print("######Get####",data.get("notify_email", ""))
    request = data.get('request')
    monitor_user = None
    if data.get('notify_email'):
        monitor_user = User.objects.filter(
            username=data.get('notify_email').lower()
        ).first()

    user_form = UserForm(data)
    profile_data = {}
    profile_data['name'] = data['name']
    profile_data['notify_email'] = data['email']
    profile_data['days_sober'] = '0'
    profile_form = UserProfileInfoForm(profile_data)
    print("user form ", user_form)
    if user_form.is_valid() and profile_form.is_valid():
        print("Enter in this form")
        user = user_form.save()
        print("UERERERE %s" % user)
        user.set_password(user.password)
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.phone = data.get("phone", "")
        profile.days_sober = data.get("days_sober", 0)
        profile.sober_date = data.get("sober_date", 0)
        profile.name = data.get("name", "")
        profile.notify_email = data.get("notify_email", "")
        profile.source = data.get("source", "")
        profile.save()

        # log user in!
        username = data.get('email')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if monitor_user:
            logger.info("I HAVE MONITOR USER")
            email_utils.send_raw_email(
                to_email=data.get("notify_email"),
                reply_to=data.get('email'),
                subject='useIAM: %s added you as a monitor'
                        % data.get('name'),
                message_text=constants.existing_monitor_message)
        elif data.get('notify_email'):
            url = "https://" + request.META['HTTP_HOST']
            url += "/create_notify_user/" + profile.user_hash
            mail_text = constants.new_monitor_message + url
            email_utils.send_raw_email(
                to_email=data.get("notify_email"),
                reply_to=data.get('email'),
                subject='useIAM: %s added you as a monitor'
                        % data.get('name'),
                message_text=mail_text)

        if user and request:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))

    elif (user_form.errors):
        return 'error'


def index(request):
    registered = False
    user_taken = False
    name = ''
    if request.method == 'POST':
        data = {k: v for k, v in request.POST.items()}
        data['request'] = request
        user = _create_user(**data)
        if user == 'error':
            user_taken = True
        else:
            return user

    user_form = UserForm()
    profile_form = UserProfileInfoForm()
    # need to get the name XXX fix this
    profile = notify_utils.get_user_profile(request.user)
    sober_days = 0
    if profile:
        name = profile.name
        sober_days = (profile.days_sober +
                      days_sober(profile.user.date_joined))

    return render(request, 'xppda/index.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'user_taken': user_taken,
                   'sober_days': sober_days,
                   'name': name,
                   'registered': registered})


def create_notify_user(request, user_hash):
    profile = get_object_or_404(UserProfileInfo, user_hash=user_hash)

    print("#######Notiy create user########")
    if request.method == 'POST':
        # username = request.POST.get('email')
        username = profile.notify_email
        password = request.POST.get('password')

        user = User.objects.filter(username=username).first()
        if user:
            return HttpResponse('Email already exists')

        user = User()
        user.email = username
        user.username = username
        user.set_password(password)
        user.save()

        profile = UserProfileInfo()
        profile.user = user
        profile.save()

        user = authenticate(username=username, password=password)
        login(request, user)

        return HttpResponseRedirect(reverse('monitor'))

    return render(
        request, 'xppda/create_notify_user.html',
        {'username': profile.notify_email}
    )


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        notify_email = request.POST.get('notify_email', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if notify_email:
                    profile = notify_utils.get_user_profile(request.user)
                    profile.notify_email = notify_email
                    profile.save()
                # update notify_email

                if request.GET.get('next'):
                    full_path = request.get_full_path()
                    val = full_path.split('next=')
                    redirect_uri = val[1]
                else:
                    redirect_uri = reverse('index')

                return HttpResponseRedirect(redirect_uri)
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            return HttpResponse("Invalid login details given")

    return render(request, 'xppda/login.html', {})
