from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailapi.models import Mail, Account


@api_view(["GET"])
def get_emails(request, to_email):
    account = Account.objects.filter(email=to_email).first()
    return Response(Mail.objects.filter(account=account).values())


@api_view(["GET"])
def get_accounts(request):
    accounts = Account.objects.filter().values("email")
    return Response(accounts)

