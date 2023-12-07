from django.urls import include, path
from mailapi import views
from rest_framework import routers

app_name = 'mailapi'


urlpatterns = [
    path('get-emails/<str:to_email>/', views.get_emails),
    path('get-accounts/', views.get_accounts),
]
