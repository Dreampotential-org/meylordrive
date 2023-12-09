from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from dappx.models import UserProfileInfo
from common import config

import json
import stripe

logger = config.get_logger()
stripe.api_key = 'sk_test_2Dri41Al1ks38qtoQvPmw1dg00gedYOg1M'


@api_view(['POST'])
def pay(request):
    token = Token.objects.get(key=request.GET.get("token"))
    logger.info("Signing up user on paid plan: %s" % token.user.email)
    stripe_token = request.data.get("stripeToken")
    stripe_plan = request.data.get("plan")

    profile = UserProfileInfo.objects.filter(
        user__username=token.user.email
    ).first()

    # if user already has a subscirption return okay.
    # TODO might be a good idea to confirm this in stripe and
    # heal the db if not.
    if profile.stripe_subscription_id:
        return JsonResponse({
            'status': 'OKAY'
        })

    # first check if customer already exists
    customers = stripe.Customer.list(email=token.user.email)
    if customers:
        customer = customers['data'][0]

    else:
        # create a new customer in stripe
        try:
            customer = stripe.Customer.create(
                source=stripe_token, email=token.user.email)
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})

            print ("Status is: %s" % e.http_status)
            print ("Type is: %s" % err.get('type'))
            print ("(Code is: %s" % err.get('code'))
            # param is '' in this case
            print ("Param is: %s" % err.get('param'))
            print ("(Message is: %s" % err.get('message'))
            return json.dumps({"error": err.get("message")})

    # put them on a plan
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{'plan': stripe_plan}])

    profile.stripe_subscription_id = subscription['id']
    profile.save()

    return JsonResponse({
        'status': 'OKAY'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_plan(request):
    logger.info("Cancelling user on paid plan: %s" % request.user.email)
    profile = UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()

    # fetch it
    response = stripe.Subscription.retrieve(profile.stripe_subscription_id)
    if response['status'] == "canceled":
        logger.info("Plan already cancelled updating db")
        profile.stripe_subscription_id = None
        profile.save()
        return JsonResponse({
            'status': 'OKAY'
        })

    response = stripe.Subscription.delete(profile.stripe_subscription_id)
    if response["status"] == "canceled":
        profile.stripe_subscription_id = None
        profile.save()
        return JsonResponse({
            'status': 'OKAY'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_plan_braintree(request):
    logger.info("Cancelling user on paid plan: %s" % request.user.email)
    profile = UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()
    profile.paying = False
    profile.iap_blurb = ''
    profile.save()
    return JsonResponse({
            'status': 'OKAY'
        })