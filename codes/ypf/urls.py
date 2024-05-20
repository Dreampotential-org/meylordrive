from django.urls import path

from . import views


urlpatterns = [
    path('createartic', views.createartic, name="createartic"),
    path('getartic/<int:articid>',
         views.getartic, name="getartic"),
    path('deleteartic/<int:getartic>', views.deleteartic,
          name="deleteartic"),
]
