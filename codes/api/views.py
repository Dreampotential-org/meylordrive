from rest_framework.decorators import api_view

from tasks.models import Project, ProjectService, ProjectCommand, Org
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_org(request):
    org = Org()
    org.name = request.data.get("name")
    org.user = request.user
    org.save()

    return Response({'id': org.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_orgs(request):
    orgs = Org.objects.filter(user=request.user)

    return Response(orgs)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_project(request):

    project = Project()
    org = Org.objects.filter(request.data.get("org_id")).first()
    project.org = org
    project.user = request.user
    project.repo = request.data.get("repo")
    project.save()

    return Response({'id': org.id})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_projects(request):
    orgs = Org.objects.filter(user=request.user)
    return Response(orgs)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_project_service(request):
    project_service = ProjectService()
    project_service.repo = request.data.get("repo")
    project_service.command = request.data.get("command")
    project_service.name = request.data.get("name")
    project_service.user = request.user
    project_service.save()

    return Response({'id': project_service.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_project_services(request):
    project_services = ProjectService.objects.filter(user=request.user)
    return Response(project_services)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_project_command(request):
    project_command = ProjectCommand()
    project_command.repo = request.data.get("repo")
    project_command.command = request.data.get("command")
    project_command.name = request.data.get("name")
    project_command.user = request.user
    project_command.save()

    return Response({'id': project_command.id})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_project_commands(request):
    project_commands = ProjectCommand.objects.filter(user=request.user)
    return Response(project_commands)


