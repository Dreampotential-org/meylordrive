from rest_framework.decorators import api_view

from tasks.models import Project, ProjectService, ProjectCommand, Org
from agent.models import ApiKey
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from tasks.models import KeyPair, ProjectMember


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_org(request, org_id):
    Org().objects.filter(id=org_id, uesr=request.user).delete()
    return Response({'message': "Okay"})


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


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_project_service(request, project_service_id):
    ProjectService.objects.filter(user=request.user,
                                  id=project_service_id).delete()
    return Response({"message": "Okay"})


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_keypairs(request):
    keypairs = KeyPair.objects.filter(user=request.user)
    return Response(keypairs)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_keypair(request, keypair_id):
    KeyPair.objects.filter(user=request.user, id=keypair_id).delete()
    return Response({"status": "Okay"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_keypair(request):
    keypair = KeyPair()
    keypair.value = request.data.get("value")
    keypair.user = request.user
    keypair.save()

    return Response({'id': keypair.id})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_member(request):
    # look up pm of user making the request
    pm = ProjectMember.objects.filter(user=request.user)
    # check user is admin or Role XXX
    if not pm.admin:
        return Response({'error': "User is not an admin of a group."})

    user = ProjectMember.objects.filter(
        id=request.data.get("member_id")
    ).first()

    # first user has to have a accout XXX
    o = Org.objects.filter(id=request.data.get("org_id")).first()
    if not o:
        return Response({'message': "Not a valid org_id"})

    # Create new OrgMember
    pm = ProjectMember()
    pm.user = user
    pm.added_by = request.user
    pm.org = o

    # Need to verify user is allowed to do such thing
    # pm.user = request.user
    pm.save()

    return Response({'id': pm.id})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_member(request, member_id):
    pm = ProjectMember.objects.filter(id=member_id)
    pm.remove()

    return Response({'status': "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_api_key(request):
    api_key = ApiKey()
    api_key.user = request.user
    api_key.save()

    return Response({'id': api_key.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_api_keys(request, member_id):
    keys = ApiKey.objects.filter(user=request.user)

    return Response(keys)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_api_key(request, api_key_id):
    ApiKey.objects.filter(id=api_key_id).delete()

    return Response({'status': "ok"})
