from django.urls import path, include
from knox import views as knox_views
from .views import UserRegister, PasswordReset, UserLogin, ChangePasswordView


urlpatterns = [
    # User Management and Auth APIs
    path('user/register/', UserRegister.as_view(), name='register'),
    path('user/login', UserLogin.as_view(), name='login'),
    path('user/logout', knox_views.LogoutView.as_view(), name='logout'),
    # path('/user/password_reset', PasswordReset.as_view(), name='reset'),
    path('user/logoutall/', knox_views.LogoutAllView.as_view(),
         name='logoutall'),
    path('user/change-password', ChangePasswordView.as_view(),
         name='change_password'),
    path('user/password_reset/', include('django_rest_passwordreset.urls',
                                         namespace='password_reset')),
]
