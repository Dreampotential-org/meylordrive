from tasks import serialize
from tasks.models import Task
from tasks.serialize import TaskSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json


class TaskDetails(APIView):
    def post(self, request):
        serializeobj = TaskSerializer(data=request.data)
        if serializeobj.is_valid():
            serializeobj.save()
            return Response(serializeobj.data, status=status.HTTP_201_CREATED)
        return Response({"message": json.dumps(serializeobj.errors)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        detailsObj = Task.objects.all()
        dlSerializeObj = TaskSerializer(detailsObj, many=True)
        return Response(dlSerializeObj.data, status=status.HTTP_200_OK)
