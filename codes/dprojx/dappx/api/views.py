from rest_framework import (viewsets, filters, status, mixins, generics)
from ..models import UserLead
from .serializers import UserLeadSerializer


class UserLeadApi(generics.CreateAPIView):
    queryset = UserLead.objects.all()
    serializer_class = UserLeadSerializer
