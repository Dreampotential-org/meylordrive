from mailapi.models import Account

import datetime
import email
import email.header
import imaplib
import sys
from utils.chirp import CHIRP
from io import StringIO

EMAIL_FOLDER = "INBOX"


def connect(email_address, password):
    CHIRP.info("Trying to connect this")
    mail_client = imaplib.IMAP4_SSL('agentstat.com')

    try:
        rv, data = mail_client.login(email_address, password)
    except imaplib.IMAP4.error:
        CHIRP.info(email_address + " LOGIN FAILED!!!")
        return

    rv, data = mail_client.select(EMAIL_FOLDER)
    if rv != 'OK':
        CHIRP.info("ERROR: Unable to open mailbox ", rv)

    return mail_client


def get_all_mails():
    accounts = Account.objects.filter()
    CHIRP.info("Number of accounts on the system %s" % len(accounts))

    mails = []
    for account in accounts:
        CHIRP.info("checking account %s" % account.email)
        mails = mails + get_mails(
            account.email, account.password, account.id
        )

    return mails


def parse_email_body(b):
    body = ""
    print(b)
    print(type((b)))
    if b.is_multipart():
        for part in b.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = b.get_payload(decode=True)

    return body


def get_mails(email_address, password, account_id):
    mail_client = connect(email_address, password)
    if not mail_client:
        CHIRP.info("Not able to login accout")
        return []

    rv, data = mail_client.search(None, "ALL")
    if rv != 'OK':

        CHIRP.info("No messages found!")
        return []

    mails = []
    for num in data[0].split():
        rv, data = mail_client.fetch(num, '(RFC822)')
        if rv != 'OK':
            CHIRP.info("ERROR getting message", num)
            return []

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(
            email.header.decode_header(msg['Subject'])
        )
        subject = str(hdr)
        CHIRP.info(msg)
        # CHIRP.info('Raw Date:', msg['Date'])

        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple)
            )
            local_date = local_date.strftime("%a, %d %b %Y %H:%M:%S")

        parsed_email = email.message_from_string(data[0][1].decode("utf-8"))
        mail = dict()
        mail['subject'] = subject
        mail['row_date'] = msg['Date']
        mail['local_date'] = local_date
        mail['message'] = msg.as_string()
        mail['account_id'] = account_id
        mail['to'] = parsed_email['to']
        mail['from'] = parsed_email['from']
        mail['body'] = parse_email_body(
            msg)
        mails.append(mail)

    mail_client.close()
    return mails
