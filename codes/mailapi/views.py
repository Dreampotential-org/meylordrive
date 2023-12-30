from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailapi.models import Mail, Account
from utils.email_utils import send_raw_email


@api_view(["POST"])
def send_email(request):

    account = Account.objects.filter(
        email=request.data.get("mail_to")
    ).first()

    if not account:
        return Response({
            "status": 'error account not found'
        })


    mail = Mail()

    send_raw_email(
        request.data.get("mail_from"),
        request.data.get("mail_to"),
        request.data.get("reply_to"),
        request.data.get("subject"),
        request.data.get("message_text"),
        request.data.get("message_html")
    )


    mail = Mail()
    mail.account = account
    mail.mail_from = request.data.get("mail_from")
    mail.mail_to = request.data.get("mail_to")
    mail.subject = request.data.get("subject")
    mail.message = request.data.get("message_text")

    mail.save()


    return Response({"status": 'okay'})


@api_view(["GET"])
def get_emails(request, to_email):
    return Response(Mail.objects.filter(mail_to=to_email).values())

@api_view(["GET"])
def get_cemails(request, to_email):
    return Response(Mail.objects.filter(mail_from=to_email).values())


@api_view(["GET"])
def set_draft(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.draft = True
        mail.save()
    return Response({"status": 'okay'})


@api_view(["GET"])
def set_undraft(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.draft = False
        mail.save()
    return Response({"status": 'okay'})


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
        mail.deleted = False
        mail.save()
    return Response({
        "status": 'okay'
    })
