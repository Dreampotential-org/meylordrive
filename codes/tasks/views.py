"""task API View."""
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

import json
import threading

from agent.management.commands import run_tasks
from tasks.models import Task, TaskLog, GithubHook, Server, Pipeline, PipelineServer
from tasks.serialize import (
    TaskSerializer,
    TaskLogSerializer,
    GithubHookSerializer,
    ServerSerializer,
    PipelineSerializer,
    PipelineServerSerializer,
)


def run_job(server_pipeline, task_log):
    ssh = run_tasks.make_ssh(server_pipeline.server)
    print(
        "Run job server: %s %s"
        % (server_pipeline.server.username, server_pipeline.server.ip_address)
    )
    run_tasks.get_repo(ssh, server_pipeline.pipeline.repo, task_log)
    run_tasks.run_log_ssh_task(
        ssh,
        server_pipeline.server,
        server_pipeline.pipeline.task,
        task_log,
        server_pipeline.pipeline.repo,
    )


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
        return Response(
            {"message": json.dumps(serializeobj.errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request):
        detailsObj = Task.objects.all()
        dlSerializeObj = TaskSerializer(detailsObj, many=True)
        return Response(dlSerializeObj.data, status=status.HTTP_200_OK)


class TaskLogView(ModelViewSet):
    """Task log  Api ViewSet."""

    serializer_class = TaskLogSerializer

    def get_queryset(self):
        """"""
        return TaskLog.objects.all()


class GithubHookDetails(APIView):
    def post(self, request, id):
        req = {"repo": str(request.data)}
        serializeobj = GithubHookSerializer(data=req)
        threads = []
        if serializeobj.is_valid():
            serializeobj.save()
            pipeline = Pipeline.objects.get(id=id)
            pipelines_servers = PipelineServer.objects.filter(pipeline=pipeline)
            for pipeline_server in pipelines_servers:
                task_log = TaskLog()
                task_log.task = pipeline.task
                task_log.file_log = f"./logs/{task_log.id}.txt"
                task_log.save()
                t = threading.Thread(target=run_job, args=(pipeline_server, task_log))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            return Response(serializeobj.data, status=status.HTTP_201_CREATED)
        return Response(
            {"message": json.dumps(serializeobj.errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ServerView(ModelViewSet):
    """Task log  Api ViewSet."""

    serializer_class = ServerSerializer

    def get_queryset(self):
        """"""
        return Server.objects.all()


class PipelineView(generics.GenericAPIView):
    serializer_class = PipelineSerializer

    def get_queryset(self):
        return Pipeline.objects.all()

    def get(self, request, *args, **kwargs):
        serialized = self.get_serializer(self.get_queryset(), many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PipelineDetailView(generics.GenericAPIView):
    serializer_class = PipelineSerializer

    def get_queryset(self):
        return Pipeline.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            try:
                pipeline = Pipeline.objects.get(id=kwargs.get("pk"))
                serialized = self.get_serializer(pipeline)
                return Response(serialized.data, status=status.HTTP_200_OK)
            except Pipeline.DoesNotExist:
                return Response("Pipeline Not Found", status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            pipeline = Pipeline.objects.get("pk")
            serialized = self.get_serializer(pipeline, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data)
            return Response(serialized.errors)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            pipeline = Pipeline.objects.get(id=kwargs.get("pk"))
            pipeline.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PipelineServerView(generics.GenericAPIView):
    serializer_class = PipelineServerSerializer

    def get_queryset(self):
        return PipelineServer.objects.all()

    def get(self, request, *args, **kwargs):
        serialized = self.get_serializer(self.get_queryset(), many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PipelineServerDetailsView(generics.GenericAPIView):
    serializer_class = PipelineServerSerializer

    def get_queryset(self):
        return PipelineServer.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            try:
                pipeline_server = PipelineServer.objects.get(id=kwargs.get("pk"))
                serialized = self.get_serializer(pipeline_server)
                return Response(serialized.data, status=status.HTTP_200_OK)
            except PipelineServer.DoesNotExist:
                return Response(
                    "Pipeline server Not Found", status=status.HTTP_404_NOT_FOUND
                )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            pipeline_server = PipelineServer.objects.get("pk")
            serialized = self.get_serializer(pipeline_server, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data)
            return Response(serialized.errors)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            pipeline_server = PipelineServer.objects.get(id=kwargs.get("pk"))
            pipeline_server.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
