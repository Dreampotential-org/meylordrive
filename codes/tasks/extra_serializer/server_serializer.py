from rest_framework import serializers

from tasks.models import Server


class ServerCallSerializer(serializers.ModelSerializer):
  server_key = serializers.ListField(
    child=serializers.IntegerField(min_value=0, max_value=1000000000)
  )

  class Meta:
    model = Server
    fields = "__all__"
