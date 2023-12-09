from dappx import email_utils
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.serializers import (
    OrganizationMemberSerializer
)
from rest_framework import response, status
from dappx.models import UserProfileInfo
from dappx.models import UserMonitor
from dappx.models import OrganizationMember, OrganizationMemberMonitor
from dappx.models import Organization
from dappx.notify_utils import notify_monitor
from dappx.views import upload_org_logo
from api.serializers import UserMonitorSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from django.db.models import Q
from django.conf import settings


class OrganizationMemberView(generics.GenericAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer

    @swagger_auto_schema(manual_parameters=[

        openapi.Parameter('search', openapi.IN_QUERY,
                          description="Search by name and email",
                          type=openapi.TYPE_STRING,
                          required=False, default=None),

    ])
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            return response.Response("Login first",
                                     status=status.HTTP_400_BAD_REQUEST)

        org = OrganizationMember.objects.filter(user_id=user.id).first()
        if not org:
            return Response("Member not in org",
                            status=status.HTTP_201_CREATED)

        search = request.GET.get('search')
        if search:
            org_member = OrganizationMember.objects.filter(
                (Q(user__first_name__icontains=search) |
                 Q(user__email__icontains=search)) & Q(
                 organization_id=org.organization_id))
        else:
            org_member = OrganizationMember.objects.filter(
                organization_id=org.organization_id)

        paginated_response = self.paginate_queryset(org_member)
        serialized = self.get_serializer(paginated_response, many=True)
        return self.get_paginated_response(serialized.data)


class UserOrganizationIDView(generics.GenericAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            return response.Response("Login first",
                                     status=status.HTTP_400_BAD_REQUEST)
        else:
            org = OrganizationMember.objects.filter(user_id=user.id).first()
            org_patient = UserMonitor.objects.filter(user_id=user.id).first()
            if org is None and org_patient is None:
                data = {"organization_id": None,
                        "Patient_org_id": None}
                return response.Response(data)
            elif org and org_patient:
                data = {"organization_id": org.organization_id,
                        "Patient_org_id": org_patient.organization_id}
                return response.Response(data)
            elif org is None and org_patient:
                data = {"organization_id": None,
                        "Patient_org_id": org_patient.organization_id}
                return response.Response(data)
            elif org and org_patient is None:
                data = {"organization_id": org.organization_id,
                        "Patient_org_id": None}

                return response.Response(data)


@api_view(['POST'])
def add_member(request):
    email = request.data['email']
    name = request.data['name']
    password = request.data['password']
    admin = request.data['admin']
    try:
        organization = request.data['organization_id']
    except KeyError:
        organization = None

    '''email = 'unitednuman@hotmail.com'
    name = 'numan'
    password = 'pass@123'
    admin = 'true'
    organization = 2'''
    email = email.lower()
    if email is None or name is None or password is None or admin is None:
        data = {
            'status': False,
            'error': 'Missing parameters'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    if admin == 'true':
        value = True
    else:
        value = False
    user = User.objects.filter(email=email).first()

    if not user:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            password=make_password(password)

        )
        UserProfileInfo.objects.create(
            user=user,
            name=name
        )
    user = User.objects.filter(username=email).first()
    if user:
        User.objects.filter(email=email).update(first_name=name)
        org_member = OrganizationMember.objects.filter(user=user).first()
        if not org_member:
            org_member = OrganizationMember()
            org_member.user = user
            org_member.admin = value
            org_member.organization_id = organization
            org_member.save()
        else:
            return Response({
                'message': 'User is already a organization member'})

    return Response("Member Added", status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_member(request):
    data = {k: v for k, v in request.data.items()}

    if data['is_superuser'] == 'true':
        value = True
    else:
        value = False

    data.pop("is_superuser")
    if not data.get('email') or not data.get('first_name'):
        return Response({
            'message': 'Missing parameters. Email and password is required'
        })

    data['email'] = data['email'].lower()
    try:
        user = User.objects.filter(id=data['id']).first()
        if user:
            if not data.get('password'):

                User.objects.filter(id=user.id).update(email=data['email'],
                                                       username=data['email'],
                                                       first_name=data['first_name'],
                                                       is_staff=value)

            else:

                User.objects.filter(id=user.id).update(email=data['email'],
                                                       username=data['email'],
                                                       first_name=data['first_name'],
                                                       is_staff=value,
                                                       password=make_password(data['password']))

        org_member = OrganizationMember.objects.filter(user=user).first()
        if not org_member:
            org_member = OrganizationMember()
            org_member.user = user
            org_member.admin = value
            org_member.save()
            return Response({'status': 'Member Added'}, 200)
        if org_member:
            OrganizationMember.objects.filter(user=user).update(admin=value)
            return Response({'status': 'Member Updated'}, 200)
    except:
        return Response({'status': 'Not Found '}, 404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request, id):
    user = User.objects.filter(id=id).first()
    if user:
        org_member = OrganizationMember.objects.filter(user_id=user.id).first()
        if org_member:
            org_member.delete()
            return Response({'status': 'Deleted'}, 200)
        else:
            return Response({'status': 'Not  Found'}, 204)
    else:
        return Response({'status': 'Not  Found'}, 204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_patient(request):
    email = request.data['email']
    name = request.data['name']
    password = request.data['password']
    try:
        organization = request.data['organization_id']
    except:
        organization = None

    '''email = 'smarttest@hotmail.com'
    name = 'smart'
    password = 'pass@123'
    '''
    email = email.lower()
    if email is None or name is None or password is None:
        data = {
            'status': False,
            'error': 'Missing parameters'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            password=make_password(password)

        )
        UserProfileInfo.objects.create(
            user=user,
            name=name
        )

    user = User.objects.filter(email=email).first()
    if user:
        user_monitor = UserMonitor.objects.filter(user=user).first()
        if not user_monitor:
            user_monitor = UserMonitor()
            user_monitor.user = user
            user_monitor.notify_email = email
            user_monitor.organization_id = organization
            user_monitor.save()
            notify_monitor(request, email)
            return Response({
                'msg': '%s is added as a patient and notified',
            }, 201)
        else:
            return Response({
                'msg': '%s is already a monitor user for you',
            }, 201)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_patient(request):
    data = {k: v for k, v in request.data.items()}

    if not data.get('email') or not data.get('first_name'):
        return Response({
            'message': 'Missing parameters. Email and name is required'
        })

    data['email'] = data['email'].lower()
    try:
        try:
            user = User.objects.filter(id=data['id']).update(
                username=data['email'],
                first_name=data['first_name'])
        except:
            pass
        try:
            u = UserMonitor.objects.filter(user_id=user.id).first()
            UserMonitor.objects.filter(id=u.id).update(
                notify_email=data['email'])
        except:
            pass

        return response.Response(status=status.HTTP_200_OK)
    except Exception:
        return response.Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def remove_patient(request):
    user = User.objects.filter(username=request.user.email).first()
    notify_email = request.data.get('notify_email')
    monitors = UserMonitor.objects.filter(user=user,
                                          notify_email=notify_email).all()
    if monitors:
        UserMonitor.objects.filter(user=user,
                                   notify_email=notify_email).delete()

    return Response({
        'status': 'okay',
    }, 201)


class UserMonitorView(generics.GenericAPIView):
    queryset = UserMonitor.objects.all()
    serializer_class = UserMonitorSerializer

    @swagger_auto_schema(manual_parameters=[

        openapi.Parameter('search', openapi.IN_QUERY,
                          description="Search by name and Email",
                          type=openapi.TYPE_STRING,
                          required=False, default=None),

    ])
    def get(self, request, *args, **kwargs):
        search = self.request.GET.get("search")
        user = request.user
        if user.is_anonymous:
            return response.Response("Login first",
                                     status=status.HTTP_400_BAD_REQUEST)

        if search:
            # xxx todo add search filter back..
            user_monitor = UserMonitor.objects.filter(
                notify_email=user.email)
        else:
            user_monitor = UserMonitor.objects.filter(
                notify_email=user.email)
        paginated_response = self.paginate_queryset(user_monitor)
        serialized = self.get_serializer(paginated_response, many=True)
        return self.get_paginated_response(serialized.data)


class UserMonitorViewDetails(generics.GenericAPIView):
    queryset = UserMonitor.objects.all()
    serializer_class = UserMonitorSerializer

    def delete(self, request, *args, **kwargs):
        if kwargs.get('id'):
            user_monitor = UserMonitor.objects.get(id=kwargs.get('id'))
            user_monitor.delete()
            return response.Response("Data Deleted",
                                     status=status.HTTP_202_ACCEPTED)
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_org_clients(request):
    user = User.objects.filter(username=request.user.email).first()
    organization_member = OrganizationMember.objects.filter(user=user).first()
    if not organization_member or not organization_member.organization:
        return Response([],
                        status=status.HTTP_201_CREATED)

    clients = UserProfileInfo.objects.filter(
        user_org=organization_member.organization).values()

    for client in clients:
        # include organization_member_monitors here
        org_monitors = OrganizationMemberMonitor.objects.filter(
            client=client['user_id']
        )
        client['org_monitors'] = []
        client['email'] = User.objects.filter(
            id=client['user_id']).first().email
        for org_monitor in org_monitors:
            profile = UserProfileInfo.objects.filter(
                user=org_monitor.user
            ).first()
            client['org_monitors'].append({
                'id': org_monitor.id,
                'email': org_monitor.user.email,
                'user_id': org_monitor.user.id,
                'name': profile.name,
            })

    return Response(clients)
    

@api_view(['POST'])
@csrf_exempt
def add_org_clients(request):
    if request.method == 'POST' and request.FILES['file']:

        name = request.POST.get('name')
        hostname = request.POST.get('hostname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        phone_no = request.POST.get('phone_no')
        
        myfile = request.FILES['file']
        save_image_name = upload_org_logo(myfile, request)
        logo_url = settings.SERVER_URL+'api/view-org-logo/'+save_image_name

        Organization.objects.create(
            name=name,
            hostname=hostname,
            logo=logo_url,
            address=address,
            city=city,
            state=state,
            phone_no=phone_no
        )

        return JsonResponse({
            'name': name,
            'hostname': hostname,
            'logo': logo_url,
            'address': address,
            'city': city,
            'state': state,
            'phone_no': phone_no
        }, status=200) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_client(request):
    user = User.objects.filter(username=request.user.email).first()
    organization_member = OrganizationMember.objects.filter(user=user).first()
    if not organization_member:
        return Response("Member not in org",
                        status=status.HTTP_201_CREATED)

    member_to_add_client = request.data['member_id']

    # look up member by id and see if they are in org
    user = User.objects.filter(id=int(member_to_add_client)).first()
    if not user:
        return Response("error not user", status=status.HTTP_201_CREATED)

    org_member_check = OrganizationMember.objects.filter(user=user).first()
    if org_member_check.organization.id != organization_member.organization.id:
        print("User not in org")
        return Response("error user not in org",
                        status=status.HTTP_201_CREATED)

    client = User.objects.filter(id=int(request.data['client_id'])).first()

    organization_member_monitor = OrganizationMemberMonitor()
    organization_member_monitor.user = user
    organization_member_monitor.client = client
    organization_member_monitor.save()

    return Response("Success Added", status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_member_client(request):
    user = User.objects.filter(username=request.user.email).first()
    organization_member = OrganizationMember.objects.filter(user=user).first()
    if not organization_member:
        return Response("Member not in org",
                        status=status.HTTP_201_CREATED)

    org_member_monitor = int(request.data['org_member_monitor'])

    # XXX todo add to activity log, notify user via email
    organization_member_monitor = OrganizationMemberMonitor.objects.filter(
        id=org_member_monitor)
    print(organization_member_monitor)
    if organization_member_monitor:
        organization_member_monitor.delete()
        return Response("Deleted Added", status=status.HTTP_201_CREATED)
    return Response("Not Found", status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_organizations(request):
    orgs = Organization.objects.all()
    resp = []
    for org in orgs:
        resp.append({'id': org.id,
                     'logo': org.logo,
                     'name': org.name})
    return Response(resp)

@api_view(['GET'])
def get_org(request):
    print(request.GET.get("id"))
    orgs = Organization.objects.filter(id=int(request.GET.get('id')))
    resp = []
    for org in orgs:
        resp.append({'id': org.id,
                     'logo': org.logo,
                     'name': org.name})
    return Response(resp)


def get_org_members(organization):
    if not organization:
        return []
    return OrganizationMember.objects.filter(
        organization=organization)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_org(request):
    profile = UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()

    ### add activit tracking

    if profile.user_org:
        # alert members user has changed profiles
        pre_org_members = get_org_members(profile.user_org)
        for org_member in pre_org_members:
            email_utils.send_raw_email(
                to_email=org_member.user.email,
                reply_to=request.user.email,
                subject='useIAM: %s has left your Organization'
                        % profile.name,
                message_text="Activity will no longer be sent to your Organization")

    # lets the user clear org
    if (request.data.get("org_id") == 'NaN'):
        profile.user_org = None
    else:
        org = Organization.objects.get(id=request.data.get("org_id"))
        profile.user_org = org

    profile.save()

    # alert members user has changed profiles
    pre_org_members = get_org_members(profile.user_org)
    for org_member in pre_org_members:
        email_utils.send_raw_email(
            to_email=org_member.user.email,
            reply_to=request.user.email,
            subject='useIAM: %s has joined your Organization'
                    % profile.name,
            message_text="Need to map member to Organization Member Monitors")

    return Response({'status': 'okay'})
