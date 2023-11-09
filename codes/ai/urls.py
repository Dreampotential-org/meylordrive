from django.urls import include, path

from ai import views

from rest_framework import routers

app_name = 'ai'

# router = routers.DefaultRouter()
# rourter.register(r'agent_list', views.agent_list)

urlpatterns = [
    path('input-chat/', views.input_chat),
    path('generate-image/', views.generate_image),
    path('get-image/<int:seed>/', views.get_image),
    path('get-requests/', views.get_requests),
]
