from mailapi.models import Account

import datetime
import email
import email.header
import imaplib
import sys

EMAIL_ACCOUNT = "test2@postgecko.com"
EMAIL_PASSWORD = "test"
EMAIL_FOLDER = "INBOX"


def connect(email_address, password):
    print("Trying to connect this")
    mail_client = imaplib.IMAP4_SSL('agentstat.com')
    print("HERE>>>")


    try:
        rv, data = mail_client.login(email_address, password)
    except imaplib.IMAP4.error:
        print(email_address + " LOGIN FAILED!!!")
        return
        #sys.exit(1)

    rv, data = mail_client.select(EMAIL_FOLDER)
    if rv != 'OK':
        print("ERROR: Unable to open mailbox ", rv)

    return mail_client


def get_all_mails():
    accounts = Account.objects.filter(active_on_server=True)
    print("There is this amount of accoutns: %s" % len(accounts))
    mails = []
    for account in accounts:
        mails = mails + get_mails(
            account.email, account.password, account.id
        )

    return mails


def get_mails(email_address, password, account_id):
    mail_client = connect(email_address, password)
    if not mail_client:
        print("Not able to login accout")
        return
    rv, data = mail_client.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return

    mails = []
    for num in data[0].split():
        rv, data = mail_client.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(
            email.header.decode_header(msg['Subject'])
        )
        subject = str(hdr)
        # print('Message %s: %s' % (num, subject))
        print('Raw Date:', msg['Date'])
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple)
            )
            local_date = local_date.strftime("%a, %d %b %Y %H:%M:%S")
            print(
                "Local Date:", local_date
            )

        mail = dict()
        mail['subject'] = subject
        mail['row_date'] = msg['Date']
        mail['local_date'] = local_date
        mail['message'] = msg.as_string()
        mail['account_id'] = account_id
        mails.append(mail)

    mail_client.close()
    return mails
