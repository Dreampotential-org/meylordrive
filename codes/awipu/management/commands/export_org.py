import pandas

from django.core.management.base import BaseCommand
from dappx.models import Organization


class Command(BaseCommand):
    help = 'Crawl Agent Links'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Starting here")
        data = Organization.objects.filter().values()
        df = pandas.DataFrame(data)
        df.to_csv('csv/lake_tax.csv', index=False)