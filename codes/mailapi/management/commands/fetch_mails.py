from django.core.management.base import BaseCommand
from mailapi import models
from utils import imap_mail


class Command(BaseCommand):
    help = 'Fetching mail from mail accounts'

    def handle(self, *args, **options):
        print("HERE si where this is called...")
        messages = imap_mail.get_all_mails()
        print("Number of messages %s" % len(messages))
        for message in messages:
            print("Got a mail subject: %s" % message['subject'])
            mail = models.Mail()
            mail.subject = message['subject']
            mail.message = message['message']
            mail.local_date = message['local_date']
            mail.row_date = message['row_date']
            mail.account_id = message['account_id']
            check = models.Mail.objects.filter(
                message_id=mail.gen_message_id()
            ).count()

            if check == 0:
                mail.save()
