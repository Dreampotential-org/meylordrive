"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from authentication import views
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# from server_websocket.routing import application as websocket_application

from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView


# from server_agent.routing import websocket_urlpatterns

schema_view = get_schema_view(
   openapi.Info(
      title="Meylorci API",
      default_version='v1',
      description="Meylorci description",
      terms_of_service="",
      contact=openapi.Contact(email="meylorci@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # path('', views.home, name='home'),
  path('admin/', admin.site.urls),
  
  path("usersystem/", include('usersystem.urls')),
    path("ai/", include('ai.urls')),
    path("accounts/", include("django.contrib.auth.urls")),  # new
    path("", include("server_websocket.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path('',include('server_websocket.urls')),
  path("storage/", include('storage.urls')),
  # path("livestats/", include('livestats.urls')),
  path("", include('api.urls')),
    # path("ws/", websocket_application),
  path('swagger<format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
  path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
  path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
