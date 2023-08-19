"""task API View."""
from django.db import transaction
from knox.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
# from agent.management.commands.run_tasks import run_task
# from django.contrib.auth.models import User

import json
import threading

from tasks.models import (
  Task,
  TaskLog,
  Server,
  TaskServer,
  KeyPair,
  ServerUserKey,
)
from tasks.serialize import (
  TaskSerializer,
  TaskLogSerializer,
  ServerSerializer,
  TaskServerSerializer,
  KeyPairSerializer,
  ServerUserKeySerializer,
)

from .extra_serializer.server_serializer import ServerCallSerializer


class Domain(APIView):
    def get(self, request):
        print(request)
        print(dir(request))
        return Response({"message": "hello"})


class TaskDetails(APIView):
    def post(self, request):
        try:
            request.data["meta"] = json.dumps(request.data["meta"])
        except KeyError:
            pass

        serializeobj = TaskSerializer(data=request.data)
        if serializeobj.is_valid():
            serializeobj.save()
            return Response(serializeobj.data, status=status.HTTP_201_CREATED)

        return Response({"message": json.dumps(serializeobj.errors)},
                        status=status.HTTP_400_BAD_REQUEST,)

    def get(self, request):
        detailsObj = Task.objects.all()
        dlSerializeObj = TaskSerializer(detailsObj, many=True)
        return Response(dlSerializeObj.data, status=status.HTTP_200_OK)


class TaskView(APIView):
    def get(self, request, pk):
        try:
            detailsObj = Task.objects.get(id=pk)
            dlSerializeObj = TaskSerializer(detailsObj)
            return Response(dlSerializeObj.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response("Task Dose Not Exist!",
                            status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            try:
                request.data["meta"] = json.dumps(request.data["meta"])
            except KeyError:
                pass
            task = get_object_or_404(Task.objects.all(), pk=pk)
            serialized = TaskSerializer(instance=task,
                                        data=request.data, partial=True)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
            response = Response(serialized.data, status=status.HTTP_200_OK)
        except Exception:
            response = Response(serialized.errors,
                                status=status.HTTP_405_METHOD_NOT_ALLOWED)
            return response

    def delete(self, request, pk):
        try:
            task_object = Task.objects.get(id=pk)
            task_object.delete()
            return Response("Task Delete Successfully!",
                            status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response("Task Dose Not Exist!",
                            status=status.HTTP_404_NOT_FOUND)


class TaskLogView(ModelViewSet):
    """Task log  Api ViewSet."""

    serializer_class = TaskLogSerializer

    def get_queryset(self):
        return TaskLog.objects.all()


class TaskTrigger(APIView):

    def post(self, request, id):
        # here is where we trigger the tasks.
        threads = []
        # look up the tas
        task = Task.objects.get(id=id)
        print("We have a task %s" % task)
        # get list of servers that are mapped to task
        task_servers = TaskServer.objects.filter(task=task)
        print("Here are the task servers: %s" % task_servers)
        for task_server in task_servers:

            # XXX create helper heut
            task_log = TaskLog()
            task_log.task = task
            task_log.file_log = f"./logs/{task_log.id}.txt"
            task_log.save()
            t = threading.Thread(target=run_task,
                                 args=(task_server.server, task, task_log))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        return Response({}, status=status.HTTP_201_CREATED)


class ServerView(generics.GenericAPIView):
    """Task log  Api ViewSet."""

    serializer_class = ServerCallSerializer
    queryset = Server.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            serializer = ServerSerializer(self.get_queryset(), many=True)
            response = Response(data=serializer.data,
                                status=status.HTTP_200_OK)
        except Exception:
            response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            serialized = self.get_serializer(data=request.data)
            if serialized.is_valid():
                request_data = {
                    "ip_address": serialized.data.get("ip_address"),
                    "username": serialized.data.get("username"),
                    "password": serialized.data.get("password"),
                    "name": serialized.data.get("name"),
                    "error": bool(serialized.data.get("error", False)),
                    "alive": bool(serialized.data.get("alive", False)),
                    "in_use": bool(serialized.data.get("in_use", False)),
                    "user": User.objects.get(pk=serialized.data.get("user"))
                }

                server_object = Server(**request_data)
                server_object.save()

                if serialized.data.get("server_key", None):
                    lst_of_server_key_pair = []
                    for item in serialized.data.get("server_key"):
                        obj = ServerUserKey(
                            server=server_object,
                            user=serialized.data.get("user"),
                            keypair=KeyPair.objects.get(pk=item),)
                        lst_of_server_key_pair.append(obj)

                ServerUserKey.objects.bulk_create(lst_of_server_key_pair)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServerDetailView(generics.GenericAPIView):
    """Server detail  Api ViewSet."""

    serializer_class = ServerSerializer
    queryset = Server.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            try:
                server = Server.objects.get(id=kwargs.get("pk"))
                serialized = self.get_serializer(server)
                server_user_key = ServerUserKey.objects.filter(
                    server=kwargs.get("pk")).all()
                server_userkey_serilizer = ServerUserKeySerializer(
                    server_user_key, many=True)
                response = {
                  "server": serialized.data,
                  "server_user_keys": server_userkey_serilizer.data
                }
                return Response(response, status=status.HTTP_200_OK)
            except Server.DoesNotExist:
                return Response("Server Not Found",
                                status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            serialized = ServerCallSerializer(data=request.data)
            if serialized.is_valid(raise_exception=True):
                server = Server.objects.get(id=kwargs.get("pk"))
            request_data = {
                "ip_address": serialized.data.get("ip_address"),
                "username": serialized.data.get("username"),
                "password": serialized.data.get("password"),
                "name": serialized.data.get("name"),
                "error": bool(serialized.data.get("error", False)),
                "alive": bool(serialized.data.get("alive", False)),
                "in_use": bool(serialized.data.get("in_use", False)),
                "user": User.objects.get(pk=serialized.data.get("user")),
                "system_specs": server.system_specs.values()
            }
            server_serializer = self.get_serializer(server, data=request_data)
            if server_serializer.is_valid():
                server_serializer.save()

            if serialized.data.get("server_key", None):
                ServerUserKey.objects.filter(server=kwargs.get('pk')).delete()

                lst_of_server_key_pair = []
                for item in serialized.data.get("server_key"):
                    obj = ServerUserKey(
                        server=server, user=request_data['user'],
                        keypair=KeyPair.objects.get(pk=item))
                    lst_of_server_key_pair.append(obj)

                ServerUserKey.objects.bulk_create(lst_of_server_key_pair)
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            server = Server.objects.get(id=kwargs.get("pk"))
            if server:
                ServerUserKey.objects.filter(server=server.id).delete()
                server.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskServerView(generics.GenericAPIView):
    serializer_class = TaskServerSerializer

    def get_queryset(self):
        return TaskServer.objects.all()

    def get(self, request, *args, **kwargs):
        serialized = self.get_serializer(self.get_queryset(), many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TaskServerDetailsView(generics.GenericAPIView):
    serializer_class = TaskServerSerializer

    def get_queryset(self):
        return TaskServer.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            try:
                task_server = TaskServer.objects.get(id=kwargs.get("pk"))
                serialized = self.get_serializer(task_server)
                return Response(serialized.data, status=status.HTTP_200_OK)
            except Exception:
                return Response(
                    "Pipeline server Not Found",
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            task_server = TaskServer.objects.get(id=kwargs.get("pk"))
            serialized = self.get_serializer(task_server, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data)
            return Response(serialized.errors)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            task_server = TaskServer.objects.get(id=kwargs.get("pk"))
            task_server.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class KeyPairView(generics.GenericAPIView):
    serializer_class = KeyPairSerializer
    queryset = KeyPair.objects.all()

    def get(self, request, *args, **kwargs):
        serialized = self.get_serializer(self.get_queryset(), many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class KeyPairViewDetailView(generics.GenericAPIView):
    serializer_class = KeyPairSerializer

    def get_queryset(self):
        return KeyPair.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            try:
                key_pair = KeyPair.objects.get(id=kwargs.get("pk"))
                serialized = self.get_serializer(key_pair)
                return Response(serialized.data, status=status.HTTP_200_OK)
            # XXX
            except Exception:
                return Response("Key pair Not Found",
                                status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            key_pair = KeyPair.objects.get(id=kwargs.get("pk"))
            serialized = self.get_serializer(key_pair, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data)
            return Response(serialized.errors)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            key_pair = KeyPair.objects.get(id=kwargs.get("pk"))
            key_pair.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ServerUserKeyView(generics.GenericAPIView):
    serializer_class = ServerUserKeySerializer
    queryset = ServerUserKey.objects.all()

    def get(self, request, *args, **kwargs):
        serialized = self.get_serializer(self.get_queryset(), many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ServerUserKeyDetailView(generics.GenericAPIView):

    serializer_class = ServerUserKeySerializer

    def get_queryset(self):
        return ServerUserKey.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            try:
                server_user_key = ServerUserKey.objects.get(
                    id=kwargs.get("pk"))
                serialized = self.get_serializer(server_user_key)
                return Response(serialized.data, status=status.HTTP_200_OK)
            # XXX why/
            except Exception:
                return Response(
                    "ServerUserKey Not Found",
                    status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            server_user_key = ServerUserKey.objects.get(id=kwargs.get("pk"))
            serialized = self.get_serializer(server_user_key,
                                             data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data)
            return Response(serialized.errors)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            server_user_key = ServerUserKey.objects.get(id=kwargs.get("pk"))
            server_user_key.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
