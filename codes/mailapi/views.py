from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailapi.models import Mail, Account, Site
from utils.email_utils import send_raw_email
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from web.settings import EMAIL_HOST_USER

@api_view(["POST"])
def add_site(request, site):

    site = Site.objects.filter(
        name=site
    ).first()

    if site:
        return Response({
            "status": 'site already in ddb'
        })


    site = Site()
    site.name = site
    site.save()

    return Response({"status": 'okay'})

@api_view(["GET"])
def list_sites(request, site):
    return Response(
        Site.objects.filter().values()
    )

@api_view(["DELETE"])
def delete_email(request, email_id):
    account = Account.objects.filter(
        id=email_id
    ).first()

    if account:
        account.delete()
        return Response({
            "status": 'ok'
        })
    return Response({"status": 'no account to delete foud'})

@api_view(["DELETE"])
def delete_site(request, site_id):
    site = Site.objects.filter(
        id=site_id
    ).first()

    if site:
        site.delete()
        return Response({
            "status": 'ok'
        })
    return Response({"status": 'no sit to delete foud'})


@api_view(["POST"])
def add_email(request, email):
    account = Account.objects.filter(email=email).first()

    if account:
        return Response({
            "status": 'email already in database'
        })

    account = Account()
    account.email = email
    account.password = str(uuid.uuid4())
    account.save()

    return Response({"status": 'okay'})

@api_view(["GET"])
def list_emails(request, site):
    return Response(
        Account.objects.filter().values()
    )

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailapi.models import Mail, Account
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailapi.models import Mail, Account

@api_view(["POST"])
def send_email(request):
    # Get email address from request data
    account_email = request.data.get("mail_to")

    # Try to find the account with the specified email
    account = Account.objects.filter(email=account_email).first()

    # If account is not found, return an error response
    if not account:
        return Response({"status": f'error: account not found for email {account_email}'})

    # Create a new Mail instance
    mail = Mail()
    mail.account = account
    mail.mail_from = request.data.get("mail_from")
    mail.mail_to = account_email  # Use the found email address
    mail.subject = request.data.get("subject")
    mail.message = request.data.get("message_text")

    # Send email using SMTP
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'shaiknadeem0591@gmail.com'
    smtp_password = 'vzviuawilbewzjir'

    msg = MIMEMultipart()
    msg['From'] = request.data.get("mail_from")
    msg['To'] = account_email
    msg['Subject'] = request.data.get("subject")

    # Attach the email body
    body = MIMEText(request.data.get("message_text"))
    msg.attach(body)

    try:
        # Establish a connection to the SMTP server
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            # Use a secure connection (TLS)
            server.starttls()

            # Log in to the SMTP server if username and password are provided
            if smtp_username:
                server.login(smtp_username, smtp_password)

            # Send the email
            server.sendmail(request.data.get("mail_from"), account_email, msg.as_string())

        # Save the email to the database
        mail.save()

        return Response({"status": 'okay'})

    except Exception as e:
        return Response({"status": f'error sending email: {str(e)}'})

@api_view(["GET"])
def get_emails(request, to_email):
    return Response(Mail.objects.filter(mail_to=to_email).values())

@api_view(["GET"])
def get_cemails(request, to_email):
    return Response(Mail.objects.filter(mail_from=to_email).values())


@api_view(["POST"])
def set_draft(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if not mail:
        mail = Mail()
        mail.id = email_id
    mail.draft = True
    mail.mail_from = request.data.get("mail_from")
    mail.mail_to = request.data.get("mail_to")
    mail.subject = request.data.get("subject")
    mail.message = request.data.get("message_text")
    mail.save()

    return Response({"status": 'okay'})


@api_view(["POST"])
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


@api_view(["POST"])
def set_read(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.read = True
        mail.save()
    return Response({"status": 'okay'})


@api_view(["POST"])
def set_unread(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.read = False
        mail.save()
    return Response({"status": 'okay'})


@api_view(["DELETE"])
def delete_email(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.deleted = True
        mail.save()
    return Response({"status": 'okay'})


@api_view(["POST"])
def undelete_email(request, email_id):
    mail = Mail.objects.filter(id=email_id).first()
    if mail:
        mail.deleted = False
        mail.save()
    return Response({
        "status": 'okay'
    })



