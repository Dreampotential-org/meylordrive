from wsgiref.util import FileWrapper
import mimetypes

import os
import re
from django.conf import settings
from django.http import JsonResponse

from .models import MediA, ProfileInfo

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from django.http.response import StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
from common import config
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


logger = config.get_logger()

@api_view(['GET'])
def get_mediA(request):
    datas = MediA.objects.filter()
    resp = []
    for data in datas:
        resp.append({'id': data.id, 'name': data.name})
    return JsonResponse(resp, safe=False)


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


@api_view(['POST'])
def create_user(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email'):
        return Response({
            'message': 'Missing parameters. Email is required'
        })

    data['email'] = data['email'].lower()
    user = User.objects.filter(username=data['email']).first()

    logger.info("Create user %s" % data)

    if user:
        return Response({'message': 'User already exists'})

    # here we create the user
    user = User()
    user.email = data['email']
    user.username = data['email']
    user.set_password(data['password'])
    user.save()

    profile = ProfileInfo()
    profile.user = user
    profile.name = data.get('name', "")
    profile.save()

    user = authenticate(username=data['email'], password=data['password'])
    login(request, user)

    user = User.objects.filter(username=data['email']).first()
    token = Token.objects.get_or_create(user=user)
    data['token'] = token[0].key

    data.pop('password')
    data['message'] = "User created"

    return Response(data)


@api_view(['POST'])
def login_user(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email') or not data.get("password"):
        return Response({
            'message': 'Missing parameters. Email / Password is required'
        })

    data['email'] = data['email'].lower()

    user = authenticate(username=data['email'], password=data['password'])
    if not user:
        return Response({
            'message': 'Invalid. Email / Password is required'
        })

    login(request, user)

    token = Token.objects.get_or_create(user=user)
    data['token'] = token[0].key

    data.pop('password')
    data['message'] = "User Login"

    return Response(data)
