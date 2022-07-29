from rest_framework import serializers
from tasks.models import (Task, TaskLog, GithubHook, Server, Pipeline, PipelineServer, KeyPair, ServerUserKey)


class TaskSerializer(serializers.ModelSerializer):
  class Meta:
    model = Task
    fields = "__all__"


class TaskLogSerializer(serializers.ModelSerializer):
  class Meta:
    model = TaskLog
    fields = "__all__"


class GithubHookSerializer(serializers.ModelSerializer):
  class Meta:
    model = GithubHook
    fields = "__all__"


class ServerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Server
    fields = "__all__"


class PipelineSerializer(serializers.ModelSerializer):
  class Meta:
    model = Pipeline
    fields = '__all__'


class PipelineServerSerializer(serializers.ModelSerializer):
  class Meta:
    model = PipelineServer
    fields = '__all__'


class KeyPairSerializer(serializers.ModelSerializer):
  class Meta:
    model = KeyPair
    fields = '__all__'


class ServerUserKeySerializer(serializers.ModelSerializer):
  class Meta:
    model = ServerUserKey
    fields = '__all__'
