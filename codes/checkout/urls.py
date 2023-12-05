from django.urls import include, path

from checkout import views

from rest_framework import routers

app_name = 'checkout'

# router = routers.DefaultRouter()
# rourter.register(r'agent_list', views.agent_list)



urlpatterns = [
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.success),
    path('cancel-subscription/', views.cancel_subscription),
    path('retrieve-subscription/', views.retrieve_subscription),
    path('cancel/', views.cancel),
   # path('webhook/', views.stripe_webhook),  # new

]
