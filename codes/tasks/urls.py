from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'task-log', views.TaskLogView, basename="task-log")

# router.register(r'server', views.ServerView, basename='server')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('/', views.Domain.as_view()),
    path('tasks/', views.TaskDetails.as_view()),
    path('tasks/<int:pk>/', views.TaskView.as_view()),
    path('api/task-trigger/<int:id>/', views.TaskTrigger.as_view()),
    path('', include(router.urls)),
    path('api/server/', views.ServerView.as_view(), name='server'),
    path('api/server/<int:pk>/',
         views.ServerDetailView.as_view(), name='server'),
    path('api/key-pair/',
         views.KeyPairView.as_view(), name='key-pair'),
    path('api/key-pair/<int:pk>/',
         views.KeyPairViewDetailView.as_view(), name='key-pair'),
    path('api/server-user-key/',
         views.ServerUserKeyView.as_view(), name='server-user-key'),
    path('api/server-user-key/<int:pk>/',
         views.ServerUserKeyDetailView.as_view(), name='server-user-key'),
]
