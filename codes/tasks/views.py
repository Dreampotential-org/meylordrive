from tasks import serialize
from tasks.models import Pipeline, Task, PipelineServer, TaskLog, SystemSpecs, Server
from tasks.serialize import TaskSerializer
from tasks.models import GithubHook
from tasks.serialize import GithubHookSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from agent.management.commands import run_tasks
import threading


def run_job(server_pipeline, task_log):
    ssh = run_tasks.make_ssh(server_pipeline.server)
    print("Run job server: %s %s" %
          (server_pipeline.server.username, server_pipeline.server.ip_address))
    run_tasks.get_repo(ssh, server_pipeline.pipeline.repo, task_log)
    run_tasks.run_log_ssh_task(ssh,
                               server_pipeline.server, server_pipeline.pipeline.task, task_log, server_pipeline.pipeline.repo)


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
        return Response({"message": json.dumps(serializeobj.errors)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        detailsObj = Task.objects.all()
        dlSerializeObj = TaskSerializer(detailsObj, many=True)
        return Response(dlSerializeObj.data, status=status.HTTP_200_OK)


class GithubHookDetails(APIView):
    def post(self, request, id):
        req = {"repo": str(request.data)}
        serializeobj = GithubHookSerializer(data=req)
        threads = []
        if serializeobj.is_valid():
            serializeobj.save()
            pipeline = Pipeline.objects.get(id=id)
            pipelines_servers = PipelineServer.objects.filter(
                pipeline=pipeline)
            for pipeline_server in pipelines_servers:
                task_log = TaskLog()
                task_log.task = pipeline.task
                task_log.file_log = f"./logs/{task_log.id}.txt"
                task_log.save()
                # do this in the background
                t = threading.Thread(
                    target=run_job, args=(pipeline_server, task_log))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            return Response(serializeobj.data, status=status.HTTP_201_CREATED)
        return Response({"message": json.dumps(serializeobj.errors)},
                         status=status.HTTP_400_BAD_REQUEST)


# XXX How to add new SErver trigger server import fingerprint
