from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.response import Response
from .serializer import RegisterSerializer,UserSerializer
from knox.models import AuthToken
from rest_framework import permissions
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.models import AuthToken
from django.contrib.auth import login
# Create your views here.




# Register User
class UserRegister(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    # def get(self, request, *args, **kwargs):
    #     return render(request, "s3_uploader/register.html")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            })
        except:
            return Response({"msg": f"This email address is already registered with us"},
                            status=status.HTTP_409_CONFLICT)


class UserLogin(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data
        # Allow login using username/email both
        try:
            data['username'] = data['email']
        except:
            pass         
        serializer = AuthTokenSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return_data = super(UserLogin, self).post(request, format=None)
        return return_data