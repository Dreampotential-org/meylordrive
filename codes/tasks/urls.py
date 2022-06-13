from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('tasks/', views.TaskDetails.as_view()),
    path('api/pipeline/<int:id>/', views.GithubHookDetails.as_view()),

]
