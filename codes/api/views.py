from django.shortcuts import render
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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def list_projects(request):

    org = Org.objects.filter(request.data.get("org_id")).first()
