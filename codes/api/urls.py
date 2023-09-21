from django.urls import path, include
from . import views

urlpatterns = [
    path('api/create-org', views.create_org),
    path('api/list-orgs', views.list_orgs),
    path('api/create-keypair', views.create_keypair),
    path('api/list-keypairs', views.get_keypairs),
]
