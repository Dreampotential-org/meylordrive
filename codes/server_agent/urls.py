# server_agent/urls.py

from django.urls import path
from .views import GetTaskView

urlpatterns = [
    path('api/get_task/<str:api_key>/', GetTaskView.as_view(), name='get_task'),
]
