from rest_framework import serializers
from tasks.models import (Server,
                          KeyPair, ServerUserKey, ProjectService)


class ProjectServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectService
        fields = "__all__"



class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"


class KeyPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyPair
        fields = '__all__'


class ServerUserKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerUserKey
        fields = '__all__'
