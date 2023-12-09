from django.urls import path

from . import views

# XXX rename to routes

urlpatterns = [
    path('api/start', views.start, name="start"),
    path('api/stop', views.stop, name="stop"),
    path('api/bulk_sync_motions', views.bulk_sync_motions, name="bulk_sync_motions"),
    path('api/session_point', views.session_point,
         name="session_point"),
    path('api/get_distances', views.get_distances,
         name="get_distances"),
    path('api/stats', views.get_session_stats, name="get_session_stats"),
    path('api/gsm_Add', views.gsm_Add, name="gsm_Add"),
    path('api/gsm_send', views.gsm_send, name="gsm_send"),

]
