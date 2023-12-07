from django.conf import settings
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.chirp import CHIRP

import smtplib
import email.utils
from email.message import EmailMessage

BODY_HTML = """\
<html>
<head></head>
<body>%s</body>
</html>
"""

def send_raw_email(from_email, to_email, reply_to, subject,
                   message_text, message_html=None):

    message_html = BODY_HTML % message_text

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.add_alternative(message_text, subtype='text')
    msg.add_alternative(message_html, subtype='html')

    # Try to send the message.
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.starttls(
            context=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                               cafile=None, capath=None))
        # smtplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(settings.EMAIL_HOST_USER,
                     settings.EMAIL_HOST_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())
        server.close()

    except Exception as e:
        CHIRP.info(f"Error: {e}")
    else:
        CHIRP.info("Email successfully sent!")
