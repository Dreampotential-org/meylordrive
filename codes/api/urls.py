from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/create-org', views.create_org),
    path('api/list-orgs', views.list_orgs),
    path('api/delete-org/<int:org_id>', views.delete_org),

    path('api/create-keypair', views.create_keypair),
    path('api/list-keypairs', views.get_keypairs),
    path('api/delete-keypair/<int:keypair_id>', views.delete_keypair),

    path("api/add_member/", views.add_member),
    path("api/list-members/", views.list_members),
    path("api/remove_member/<int:member_id>", views.remove_member),


    path('api/project', views.create_project),
    path('api/list-projects', views.list_projects),
    path('api/delete-org/<int:org_id>', views.delete_org),


    path('api/create-project-command', views.create_project_command),
    path('api/list-project-commands', views.list_project_commands),
    path('api/delete-project_command/<int:project_service_id>',
         views.delete_project_service),


    path('api/project-sevice', views.create_project_service),
    path('api/list-project-services', views.list_project_services),
    path('api/delete-project_service/<int:project_service_id>',
         views.delete_project_service),

    path('api/create-api-key', views.create_api_key),
    path('api/list-api-keys', views.list_api_keys),
    path('api/delete-api-key/<int:api_key_id>', views.delete_api_key),



    path('api/project-command', views.create_project_command),
    path('api/list-project-service-commands/<int:project_service_id>',
         views.list_project_service_commands),
    path('api/list-project-commands', views.list_project_commands),
    path('api/delete-project-command/<int:project_command_id>',
         views.delete_project_command),

    path('api/server', views.create_server),
    path('api/list-servers', views.list_servers),
    path('api/delete-server/<int:server_id>', views.delete_server),
    path('api/stats', views.stats_entry),


    path('api/server-group', views.create_server_group),
    path('api/list-server-groups', views.list_server_groups),
    path('api/delete-server-group/<int:server_group_id>',
         views.delete_server_group),

]
