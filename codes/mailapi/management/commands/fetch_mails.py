import email
from django.core.management.base import BaseCommand
from mailapi import models
from utils import imap_mail
import time
from utils.chirp import CHIRP
import os

from mailapi.models import Account


def create_accounts():
    accounts = Account.objects.filter()
    CHIRP.info("creating this amout of accouts: %s" % len(accounts))
    for account in accounts:
        CHIRP.info("doing something for %s" % account.email)
        os.system(
            "/data/dreampotential/imap-service/docker-mailserver/setup.sh email add %s %s"
            % (account.email, account.password))


class Command(BaseCommand):
    help = 'Fetching mail from mail accounts'

    def handle(self, *args, **options):
        create_accounts()
        CHIRP.info("HERE si where this is called...")
        while True:
            # XXX how to avoid fetching all the emails everytime?

            messages = imap_mail.get_all_mails()
            CHIRP.info("Number of messages %s" % len(messages))

            for message in messages:
                CHIRP.info(message)
                CHIRP.info(
                    "Got a mail subject: %s"
                    % message['subject']
                )

                mail = models.Mail()
                mail.subject = message['subject']
                mail.message = message['message']
                mail.local_date = message['local_date']
                mail.row_date = message['row_date']
                mail.account_id = message['account_id']
                mail.mail_to = message['to']
                mail.mail_from = message['from']
                mail.body = message['body']

                # XXX make bulk query faster
                check = models.Mail.objects.filter(
                    message_id=mail.gen_message_id()
                ).count()

                if check == 0:
                    mail.save()
            time.sleep(2)
