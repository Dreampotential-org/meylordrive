from rest_framework import serializers
from ..models import UserLead


class UserLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLead
        fields = ['phone', 'name', 'website', 'email', 'created_at']
        read_only_fields = ['created_at']
