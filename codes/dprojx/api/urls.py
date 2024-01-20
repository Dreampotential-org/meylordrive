from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from api import views
from api import views_admin
from api import views_stripe
from api import views_orgs

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'user-profiles', views.UserProfileViewSet)
router.register(r'gps-checkin', views.GpsCheckinViewSet)
router.register(r'video', views.VideoUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # path('login-code/', views.login_code, name='login_code'),
    path('create-user/', views.create_user, name='create_user'),
    path('set-note/', views.set_note, name='set_note'),
    path('login-user-code/', views.login_user_code, name='login_user_code'),
   # path('create-user-code/', views.create_user_code,
   #       name='create_user_code'),
    path('pay/', views_stripe.pay, name='pay'),
    path('cancel-plan/', views_stripe.cancel_plan, name='cancel_plan'),
    path('cancel-plan-braintree/', views_stripe.cancel_plan_braintree,
         name='cancel_plan_braintree'),
    path('video-upload/', views.video_upload, name='video_upload'),
    path('profile/', views.profile, name='profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    path('add-monitor/', views.add_monitor, name='add_monitor'),
    path('remove-monitor/', views.remove_monitor, name='remove_monitor'),
    path('review-video/', views.review_video, name='review_video'),
    path('view-org-logo/<str:name>/', views.view_org_logo, name='view_org_logo'),
    path('get-activity/', views.get_activity, name='get_activity'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    path('get-video-info/', views.get_video_info, name='get_video_info'),
    path('list_organizations/', views_orgs.list_organizations,
         name='list_organizations'),
    path('set-org/', views_orgs.set_org, name='set_org'),
    path('get-last-patient-event/', views_admin.get_last_patient_event,
          name='get_last_patient_event'),
    path('list-patients/', views_admin.list_patients, name='list_patients'),
    path('list-patient-events/', views_admin.list_patient_events,
         name='list_patient_events'),
    path('list-patient-events-v2/', views_admin.list_patient_events_v2,
         name='list_patient_events_v2'),
    path(r'send-magic-link/', views.send_magic_link),
    path(r'auth-magic-link/', views.auth_magic_link),

    path('add_organization_member/',
         views.add_organization_member, name='add_organization_member'),

    path(r'add_member/', views_orgs.add_member),
    path('get_member/', views_orgs.OrganizationMemberView.as_view(), name='get_member'),
    path('remove_member/<int:id>', views_orgs.remove_member, name='remove_member'),
    #path('search_member/<str:name>', views_orgs.search_member, name='search_member'),
    path('edit_member/', views_orgs.edit_member, name='edit_member'),

    path(r'add_patient/', views_orgs.add_patient, name='add_patient'),
    path('edit_patient/', views_orgs.edit_patient, name='edit_patient'),
    path('list-patients-v3/', views_orgs.UserMonitorView.as_view(), name='list_patients'),
    path('list-patients-v3/<int:id>', views_orgs.UserMonitorViewDetails.as_view(), name='list_patients'),

    path('get_organization_id/', views_orgs.UserOrganizationIDView.as_view(), name='get_organization_id'),
    path('list-org-client/', views_orgs.list_org_clients, name='list_org_clients'),
    path('add-org-client/', views_orgs.add_org_clients, name='add_org_clients'),
    path('get_org/', views_orgs.get_org, name='get_org'),
    path('add-member-client/',
          views_orgs.add_member_client, name='add_member_client'),
    path('delete-member-client/',
          views_orgs.delete_member_client, name='delete_member_client'),
]
