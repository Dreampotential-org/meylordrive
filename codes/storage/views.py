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

from storage.models import Upload
from storage import video_utils
import mimetypes
from django.http.response import StreamingHttpResponse
from wsgiref.util import FileWrapper


def convert_file(uploaded_file_url):
    outfile = "%s.mp4" % uploaded_file_url.rsplit(".", 1)[0]
    command = (
        'avconv -i ./%s -codec copy ./%s' % (uploaded_file_url, outfile)
    )
    print(command)
    os.system(command)
    return outfile


def convert_and_save_video(myfile, request):
    user = request.user
    fs = FileSystemStorage()
    no_user = False

    try:
        key = user.email
    except AttributeError:
        key = "anonymous_user"
        no_user = True

    user_hash = hashlib.sha1(
        key.encode("utf-8")
    ).hexdigest()

    # WE need to update this and make it more simple

    os.makedirs('/opt/%s/', user_hash)
    uploaded_name = (
        "/opt/%s/%s-%s" % (user_hash, uuid.uuid4(), myfile.name)
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

    upload = Upload.objects.create(
        Url=uploaded_file_url, user=user,
        source=request.data.get("source")
    )

    CHIRP.info("upload response is: %s" % upload.id)

    return upload

from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def video_upload(request):
    CHIRP.error("I am here video_upload")
    CHIRP.error(request.FILES)
    CHIRP.error(request.data)
    video = request.data.get('video')
    # XXX should not be called video
    if not video:
        CHIRP.error("no video file found")
        return Response({'message': 'video is required'}, 400)

    video = convert_and_save_video(video, request)
    return Response({'id': video.id})


@api_view(['GET'])
def stream_video(request, video_id):
    upload = Upload.objects.filter(id=video_id).first()

    # XXX We need to detect the type of file a upload is and do
    # different behav based on content
    path = settings.BASE_DIR + upload.path
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


