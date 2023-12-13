from rest_framework import serializers
from .models import *

class SessionPointserializer(serializers.Serializer):
    class Meta:
        models = SessionPoint
        fields ='__all__'
