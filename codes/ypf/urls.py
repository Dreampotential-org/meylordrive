from django.urls import path

from . import views


urlpatterns = [
    path('createartic', views.createartic, name="createartic"),
    path('getartics', views.getartics, name="getartics"),
    path('getartic/<int:articid>',
         views.getartic, name="getartic"),
    path('deleteartic/<int:getartic>', views.deleteartic,
          name="deleteartic"),
     path('articles/', views.listartic, name='list_articles'),  # Map the listartic view function to the 'articles/' endpoint

]
