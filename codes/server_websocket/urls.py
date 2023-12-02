from django.urls import path, include
from .views import ThreadView

urlpatterns = [
    path('<str:username>/', ThreadView.as_view())
]