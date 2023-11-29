from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from livestats.models import JsError

@api_view(["POST"])
def jserror(request):
    print(request.data)
    je = JsError()
    je.message = request.data.get("message")
    je.url = request.data.get("url")
    je.lineNo = request.data.get("lineNo")
    je.columnNo = request.data.get("columnNo")
    je.error_msg = request.data.get("error_msg")
    je.save()

    return Response({'message': "Okay"})
