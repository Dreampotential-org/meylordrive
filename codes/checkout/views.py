import os

import stripe
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from utils.chirp import CHIRP


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stripe_config(request):
    if request.method == 'GET':
        # Get the Stripe public key from Django settings.
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session_id = request.GET.get("session_id")

    # Retrieve session data, customer_id and customer_email
    session = stripe.checkout.Session.retrieve(session_id)
    customer_id = session["customer"]
    CHIRP.info("success stripe customer id is: %s" % customer_id)
    customer_email = session['customer_details']["email"].replace(
        "%40", "@")

    # Initialize the agent model and save new customer_id to it.
    user_profile = UserProfile.objects.filter(user=request.user)
    if not user_profile:
        user_profile = UserProfile()
        user_profile.user = request.user
    user_profile.customer_id = customer_id
    user_profile.save()

    return HttpResponseRedirect("https://ai.dreampotential.org/")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    user_profile = UserProfile.objects.filter(user=request.user)
    if not user_profile:
        user_profile = UserProfile()
        user_profile.user = request.user
        user_profile.save()

    # Setup domain_url
    domain_url = os.getenv('DOMAIN_URL', 'https://api.dreampotential.org')
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id if request.user.is_authenticated else None,
            subscription_data ={
                "trial_settings": {"end_behavior": {"missing_payment_method": "pause"}},
                "trial_period_days": 7,},
            success_url=domain_url + '/checkout/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/checkout/cancel/',
            payment_method_types=['card'],
            payment_method_collection="always",
            mode='subscription',
            customer_email = request.user,
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                }
            ]
        )
        # Return the session ID as a JSON response.
        return JsonResponse({'sessionId': checkout_session['id']})
    except Exception as e:
        # Return an error message in case of an exception.
        return JsonResponse({'error': str(e)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user_profile = UserProfile.objects.filter(user=request.user)
    if not user_profile:
        user_profile = UserProfile()
        user_profile.user = request.user
        user_profile.save()

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Get list of subscription under an Agent based on customer_id
        subscription = stripe.Subscription.list(
            customer=agent_web.customer_id, status="active")

        CHIRP.info(subscription)
        subscription_id = subscription.data[0]["id"]

        # Cancel the subscription based on subscription_id
        cancellation = stripe.Subscription.delete(subscription_id)
        CHIRP.info(f"cancellation ================> {cancellation}")

        return_string = f'Your subscription has been cancelled, {request.user.email}!'
        return HttpResponse(return_string)
    except Exception as e:
        CHIRP.error(f"Cancellation failed, no subscription {e}")

        # Return an error message in case of cancellation failure.
        return_string = f'Cancellation failed, no subscription, {request.user.email}!'
        return HttpResponse(return_string)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_subscription(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        customer_ = stripe.Customer.list(email=request.user.email)
        status_ = "false"
        retrieve_sub = stripe.Subscription.list(
            customer=customer_["data"][0]["id"])
        CHIRP.info("E#ER")
        CHIRP.info(retrieve_sub["data"])
        if retrieve_sub["data"][0]["status"] in ["trialing", "active"]:
            status_ = "true"
        return JsonResponse({"subscription": status_})
    except Exception as e:
        CHIRP.error(f"Subscription already exists: Error: {e}")
        return JsonResponse({"subscription": "false"})


@api_view(["GET"])
def cancel(request):
    domain_url = os.getenv('DOMAIN_URL',
                           'https://api.dreampotential.org')
    if request.method == 'GET':
        return HttpResponseRedirect(domain_url)
