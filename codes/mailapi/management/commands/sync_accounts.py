from django.core.management.base import BaseCommand
import subprocess

from mailapi.models import Account


class Command(BaseCommand):
    help = 'Syncing email accounts'

    def handle(self, *args, **options):
        accounts = Account.objects.filter(active_on_server=False)
        password_lines = ''
        accounts_list = []
        for account in accounts:
            cmd = 'doveadm pw -s SHA512-CRYPT -p'.split()
            cmd.append(account.password)
            output = subprocess.check_output(cmd)
            output = output.decode('utf-8')
            account.active_on_server = True
            account.hash_password = output
            account.save()
            password_lines += account.email + '|' + output
            accounts_list.append(account.email + ' ' + account.password)

        self.stdout.write(','.join(accounts_list))
