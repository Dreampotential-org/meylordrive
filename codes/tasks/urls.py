from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'task-log', views.TaskLogView, basename="task-log")
router.register(r'server', views.ServerView, basename='server')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('tasks/', views.TaskDetails.as_view()),
    path('api/githubhoook/<int:id>/', views.GithubHookDetails.as_view()),
    path('', include(router.urls)),
    path('api/pipeline/',views.PipelineView.as_view(),name='pipeline'),
    path('api/pipeline/<int:pk>/',views.PipelineDetailView.as_view(),name='pipeline'),
    path('api/pipeline-server/', views.PipelineServerView.as_view(), name='pipeline-server'),
    path('api/pipeline-server/<int:pk>/', views.PipelineServerDetailsView.as_view(), name='pipeline-server')
]
