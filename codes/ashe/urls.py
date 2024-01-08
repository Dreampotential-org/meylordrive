from django.urls import path

from . import views

# XXX rename to routes

urlpatterns = [
    path('start', views.start, name="start"),
    path('stop', views.stop, name="stop"),
    path('devices', views.devices, name="devices"),
    path('bulk_sync_motions', views.bulk_sync_motions, name="bulk_sync_motions"),
    path('session_point', views.session_point,
         name="session_point"),
    path('get_distances', views.get_distances,
         name="get_distances"),
    path('stats', views.get_session_stats, name="get_session_stats"),
    path('gsm_Add', views.gsm_Add, name="gsm_Add"),
    path('gsm_send', views.gsm_send, name="gsm_send"),

]
