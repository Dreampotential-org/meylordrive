import re
from email.mime.text import MIMEText
import boto3

from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError

BODY_HTML = """\
<html>
<head></head>
<body>%s</body>
</html>
"""


def send_raw_email(to_email, reply_to, subject,
                   message_text, message_html=None):

    message_html = BODY_HTML % message_text
    message_text = message_html
    BODY_TEXT = re.sub('<[^<]+?>', '', message_html)

    SENDER = "useIAM <no-reply@useiam.com>"
    msg = MIMEMultipart('mixed')
    msg.set_charset("utf-8")
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = to_email
    msg['Reply-to'] = reply_to

    CHARSET = "utf-8"
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(message_html.encode(CHARSET), 'html', CHARSET)

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # attachmensts
    # XXX remove hard coded client
    client = boto3.client(
        'ses', aws_access_key_id='AKIARWLPGYIKWTF4OEPZ',
        aws_secret_access_key='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',
        region_name='us-east-2')
    try:
        print(
            client.send_raw_email(
                RawMessage={'Data': msg.as_string()},
                Source=SENDER, Destinations=[to_email]))
    except Exception as e:
        print("ERROR here!@!!! %s" % e)


def send_email(to_email, subject, message):
    SENDER = "useIAM <no-reply@useiam.com>"
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = to_email

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-2"

    # The subject line for the email.
    SUBJECT = subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = message

    # The character encoding for the email.
    CHARSET = "UTF-8"
    ACCESS_KEY = 'AKIARWLPGYIKWTF4OEPZ'
    SECRET_KEY = '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'

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY,
                          region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
