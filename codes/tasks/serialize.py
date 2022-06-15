from django.db.models import fields
from rest_framework import serializers
from tasks.models import Task
from tasks.models import GithubHook


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class GithubHookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubHook
        fields = "__all__"
