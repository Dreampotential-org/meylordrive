from django.urls import include, path
from mailapi import views
from rest_framework import routers

app_name = 'mailapi'


urlpatterns = [
    path('get-emails/<str:to_email>/', views.get_emails),
    path('get-accounts/', views.get_accounts),
    path('set-read/<int:email_id>/', views.set_read),
    path('set-unread/<int:email_id>/', views.set_unread),
    path('delete-email/<int:email_id>/', views.delete_email),
    path('undelete-email/<int:email_id>/', views.undelete_email),
]
