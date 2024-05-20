from struct import calcsize
import arrow
from datetime import datetime
import json
from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes

from rest_framework.permissions import IsAuthenticated
from django.core.serializers import serialize

from django.http import HttpResponse
from rest_framework import status
import requests
import json

from ypf.models import Artic


@api_view(['POST'])
def createartic(request):
    artic = Artic()
    artic.title = request.data.get("title")
    artic.message = request.data.get("message")
    artic.save()

    return Response({'id': artic.id})


@api_view(['GET'])
def getartic(request, articid):
    # here we calculate on server side..
    artic = Artic.objects.filter(id=articid).first()
    return Response(artic)


@api_view(['GET'])
def getartics(request):
    # XXX add pagination
    artics = Artic.objects.filter().values()
    return Response(artics)


@api_view(['DELETE'])
def deleteartic(request, articid):
    artic = Artic.objects.filter(id=articid).delete()
    return Response(artic)
@api_view(['GET'])
def listartic(request):
    articles = Artic.objects.all()

    data = [{"id": article.id, "title": article.title, "created_at": article.created_at, "message": article.message} for article in articles]

    return Response(data)