from django.urls import include, path

from ai import views

from rest_framework import routers

app_name = 'ai'

# router = routers.DefaultRouter()
# rourter.register(r'agent_list', views.agent_list)



urlpatterns = [
    path('generate-description/', views.generate_description),
    path('generate-image/', views.generate_image),
    path('get-image/<int:seed>/', views.get_image),
    path('get-requests/', views.get_requests),
]
