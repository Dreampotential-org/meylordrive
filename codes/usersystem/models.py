
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from  . import email_utils


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Link to password reset page
    #SERVER_URL = "https://teacher.dreampotential.org"
    SERVER_URL = "http://localhost:8000"

    reset_url = "{}/index.html?token={}".format(SERVER_URL, reset_password_token.key)


    email_plaintext_message = f'''To reset your password, visit the following link: {reset_url}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''

    email_utils.send_email(
        reset_password_token.user.email,
        "Password Reset for {title}".format(title="Website title"),
        email_plaintext_message)

    return send_mail(
        # title:
        "Password Reset for {title}".format(title="Website title"),
        # message:
        email_plaintext_message,
        # from:
        "mail-api@dreampotential.org",
        # to:
        [reset_password_token.user.email]
    )