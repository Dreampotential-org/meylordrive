from django.urls import include, path
from mailapi import views
from rest_framework import routers

app_name = 'mailapi'


urlpatterns = [
    path('add-site/<str:site>/', views.add_site),
    path('add-email/<str:email>/', views.add_email),
    path('send_email/', views.send_email, name='send_email'),
    path('get-emails/<str:to_email>/', views.get_emails),
    path('get-cemails/<str:to_email>/', views.get_cemails),
    path('get-accounts/', views.get_accounts),
    path('set-read/<int:email_id>/', views.set_read),
    path('set-draft/<int:email_id>/', views.set_draft),
    path('set-undraft/<int:email_id>/', views.set_undraft),
    path('set-unread/<int:email_id>/', views.set_unread),
    path('delete-email/<int:email_id>/', views.delete_email),


    path('list-sites/', views.list_sites),
    path('list-emails/', views.list_emails),
    path('delete-site/<int:site_id>/', views.delete_site),
    path('delete-email/<int:email_id>/', views.delete_email),
]
