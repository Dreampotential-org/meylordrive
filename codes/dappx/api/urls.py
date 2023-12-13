from django.urls import path, include
from .views import UserLeadApi

urlpatterns = [
    path("lead/", UserLeadApi.as_view())
]