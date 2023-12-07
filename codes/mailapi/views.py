from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailapi.models import Mail, Account


@api_view(["GET"])
def get_emails(request, to_email):
    return Response(Mail.objects.filter(mail_to=to_email).values())


@api_view(["GET"])
def get_accounts(request):
    accounts = Account.objects.filter().values("email")
    return Response(accounts)

