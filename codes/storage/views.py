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

from storage.models import Upload, Comment
from storage import video_utils
import mimetypes
from django.http.response import StreamingHttpResponse
from wsgiref.util import FileWrapper
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

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
        'avconv -i ./%s -codec copy ./%s' % (uploaded_file_url,
                                             outfile)
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

    # XXX TODO need to make Upload know about other metadata like video length
    upload = Upload.objects.create(
        Url=uploaded_file_url, user=user,
        source=request.data.get("source"),
        filename=myfile.name,
        file_type=myfile.name.split(".")[-1])

    CHIRP.info("upload response is: %s" % upload.id)

    return upload



@api_view(['GET'])
def list_files(request):
    try:
        key = request.user.email
        user = User.objects.get(id=request.user.id)
    except AttributeError:
        user = None


    CHIRP.info("listing files as %s" % user)
    # XXX pagination api
    res = Upload.objects.filter(
        user=user,
    ).values()
    return Response(res)



@api_view(['POST'])
@csrf_exempt
def file_upload(request):
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
def stream_video(request, video_id):
    upload = Upload.objects.filter(id=int(video_id)).first()
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


