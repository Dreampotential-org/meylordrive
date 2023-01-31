from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('<path:resource>', views.get_domain),
]
