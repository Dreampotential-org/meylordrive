from django.shortcuts import render
from rest_framework.decorators import api_view
from livestats.models import JsError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def jserror(request):

    print(request.data)
    je = JsError()
    js.message = request.data.get("message")
    js.url = request.data.get("url")
    js.lineNo = request.data.get("lineNo")
    js.columnNo = request.data.get("columnNo")
    js.error_msg = request.data.get("error_msg")
    js.save()

    return Response({'message': "Okay"})
