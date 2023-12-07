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


@api_view(["GET"])
def set_read(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.read = True
        mail.save()
    return Response({"status": 'okay'})


@api_view(["GET"])
def set_unread(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.read = False
        mail.save()
    return Response({"status": 'okay'})


@api_view(["GET"])
def delete_email(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.deleted = True
        mail.save()
    return Response({"status": 'okay'})


@api_view(["GET"])
def undelete_email(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.deleted = True
        mail.save()
    return Response({
        "status": 'okay'
    })
