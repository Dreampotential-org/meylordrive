from django.urls import path, include
from . import views

urlpatterns = [
    path('api/create-org', views.create_org),
    path('api/list-orgs', views.list_orgs),
    path('api/delete-org/<int:org_id>', views.delete_org),

    path('api/create-keypair', views.create_keypair),
    path('api/list-keypairs', views.get_keypairs),
    path('api/delete-keypair/<int:keypair_id>', views.get_keypairs),

    path("api/add_member/", views.add_member),
    path("api/remove_member/<int:member_id>", views.remove_member),


    path('api/project', views.create_project),
    path('api/list-projects', views.list_projects),
    path('api/delete-org/<int:org_id>', views.delete_org),


    path('api/project-sevice', views.create_project_service),
    path('api/list-project-services', views.list_project_services),
    path('api/delete-project_service/<int:project_service_id>', views.delete_project_service),



]
