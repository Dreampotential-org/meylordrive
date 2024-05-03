from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import os
import hashlib
import uuid
from utils.chirp import CHIRP

from storage.models import Upload, Comment, View
from storage import video_utils
import mimetypes
from django.http.response import StreamingHttpResponse
from wsgiref.util import FileWrapper
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from wsgiref.util import FileWrapper
import mimetypes

import os
import re
from django.conf import settings
from django.http import JsonResponse

from .models import  MediA, ProfileInfo, YouTubeVideo

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from django.http.response import StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
from common import config
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from spotify.models import *

from ashe.models import Device, Session


@api_view(['GET'])
def add_view(request, upload_id):
    view = View()
    try:
        view.user = request.user
    except (AttributeError, ValueError):
        pass

    upload = Upload.objects.filter(
        id=upload_id).first()

    if not upload:
        return Response({
            'error': "no id %s" % request.data.get("upload_id")})
    view.upload = upload
    view.save()
    return Response({'status': 'okay'})

@api_view(['POST'])
def add_comment(request):
    comment = Comment()
    upload = Upload.objects.filter(
        id=int(request.data.get("upload_id"))).first()

    if not upload:
        return Response({
            'error': "no id %s" % request.data.get("upload_id")})

    comment.upload = upload
    comment.message = request.data.get("message")

    try:
        comment.user = request.user
    except (AttributeError, ValueError):
        pass

    comment.save()

    return Response({'status': 'okay'})

@api_view(['GET'])
def list_comments(request, upload_id):
    comments = Comment.objects.filter(
        upload__id=int(upload_id)).values()

    return Response(comments)


def convert_file(uploaded_file_url):
    outfile = "%s.mp4" % uploaded_file_url.rsplit(".", 1)[0]

    command = (
        'ffmpeg -i %s -vcodec h264 -acodec aac %s' % (
            uploaded_file_url, outfile)
    )

    print(command)
    os.system(command)
    return outfile


def convert_and_save_file(myfile, request):
    user = request.user
    fs = FileSystemStorage()
    no_user = False

    try:
        key = user.email
        CHIRP.info("Uploading file as user %s" % user.email)
    except AttributeError:
        key = "anonymous_user"
        no_user = True

    user_hash = hashlib.sha1(
        key.encode("utf-8")
    ).hexdigest()

    # WE need to update this and make it more simple

    try:
        os.makedirs('/data/meylor-uploads/%s/' % user_hash)
    except FileExistsError:
        pass
    uploaded_name = (
        "/data/meylor-uploads/%s/%s.%s" % (user_hash,
                                           uuid.uuid4(),
                                           myfile.name.split(".")[-1])
    ).lower()

    filename = fs.save(uploaded_name, myfile)
    uploaded_file_url = fs.url(filename)

    if uploaded_name[-4:] == '.mov':
        # ffmpeg!
        uploaded_file_url = convert_file(uploaded_file_url)
    # XXX resize video for android need to implement async processing

    CHIRP.info("Uploaded video file: %s" % uploaded_file_url)
    if not no_user:
        # now lets create the db entry
        user = User.objects.get(id=user.id)
    else:
        user = None

    CHIRP.info("the user for this uploaded file is %s" % user)


    # get the session and device
    session = Session.objects.filter(
        token=request.headers.get("Authorization")
    ).first()

    session.device

    # XXX other metadata like video length

    upload = Upload.objects.create(
        device=session.device,
        Url=uploaded_file_url,
        user=user,
        source=request.data.get("source"),
        filename=myfile.name,
        file_type=myfile.name.split(".")[-1])

    CHIRP.info("upload response is: %s" % upload.id)

    return upload



# @api_view(['GET'])
# def list_files(request):
#     try:
#         key = request.user.email
#         user = User.objects.get(id=request.user.id)
#     except AttributeError:
#         user = None


#     CHIRP.info("listing files as %s" % user)
#     # XXX pagination api
#     res = Upload.objects.filter(
#         user=user,
#     ).values()
#     return Response(res)

from django.db.models import Count

@api_view(['GET'])
def getfiles(request):

    # get the session and device
    session = Session.objects.filter(
        token=request.headers.get("Authorization")
    ).first()
    CHIRP.info(session)
    CHIRP.info(request.headers.get("Authorization"))
    session.device

    CHIRP.info("device getfiles%s" % session.device)
    # Annotate each upload with the count of associated comments
    uploads_with_comments_count = Upload.objects.filter(
        device=session.device
        # user=user,
    ).annotate(comments_count=Count('comment')).values()

    paginator = PageNumberPagination()
    paginator.page_size = 25

    page = paginator.paginate_queryset(
        uploads_with_comments_count, request
    )
    if page is not None:
        return paginator.get_paginated_response(page)


@api_view(['GET'])
def get_activity(request):
    # XXX We need to add pagination into db
    # XXX we need to add some way to filter and control sorting
    uploads_with_comments_count = Upload.objects.filter(
    ).annotate(comments_count=Count('comment')).values()

    paginator = PageNumberPagination()
    paginator.page_size = 25

    page = paginator.paginate_queryset(uploads_with_comments_count, request)
    if page is not None:
        return paginator.get_paginated_response(page)



@api_view(['POST'])
@csrf_exempt
def fileupload(request):
    CHIRP.error(request.FILES)
    CHIRP.error(request.data)
    file = request.data.get('file')

    # XXX should not be called video
    if not file:
        CHIRP.error("no file found")
        return Response({'message': 'file is required'}, 400)

    file = convert_and_save_file(file, request)
    return Response({'id': file.id})


@api_view(['GET'])
def stream(request):
    upload = Upload.objects.filter(id=int(request.GET.get("id"))).first()
    if not upload:
        return Response("Not Found")

    # XXX We need to detect the type of file a upload is and do
    # different behav based on content
    path = "/data" + upload.Url
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




from wsgiref.util import FileWrapper
import mimetypes




logger = config.get_logger()

@csrf_exempt
@api_view(['GET'])
def get_media(request):
    videos = YouTubeVideo.objects.all()
    resp = []

    for video in videos:
        resp.append({
            'id': video.id,
            'title': video.title,
            'url': video.url,
            'description': video.description,
        })

    return JsonResponse(resp, safe=False, json_dumps_params={'indent': 2})


def stream_mediA(request):
    data = MediA.objects.get(id=request.GET.get("id"))
    return stream_video(request, data.path)


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):

        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request):
    print("HERE WE in are")
    path = "%s" % MediA.objects.get(id=request.GET.get("id")).path
    print(path)
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
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
        resp = StreamingHttpResponse(RangeFileWrapper(
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


def list_downloaded_songs(request):
    downloaded_songs = DownloadedSong.objects.all()
    song_names = [f"{song.song.artist_name} - {song.song.track_title}"
                  for song in downloaded_songs]
    return JsonResponse({'downloaded_songs': song_names})
