from rest_framework import serializers
from tasks.models import (Task, TaskLog, Server, TaskServer,
                          KeyPair, ServerUserKey)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = "__all__"


class TaskTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"


class TaskServerSerializer(serializers.ModelSerializer):
    key_pair = serializers.JSONField()

    class Meta:
        model = TaskServer
        fields = '__all__'


class KeyPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyPair
        fields = '__all__'


class ServerUserKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerUserKey
        fields = '__all__'
