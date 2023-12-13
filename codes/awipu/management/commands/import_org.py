import pandas
import requests
import hashlib
import uuid
import os
import csv

from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from dappx.models import Organization
from django.conf import settings


class Command(BaseCommand):
    help = 'Import organisations'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Starting here")

        path = '/Users/hassan/Desktop/development/useiam/djangox/csv/lake_tax_import.csv'
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] != 'name':
                    print(row[0])


                    # url = 'https://m.useiam.com/img/elevaterehab.png'
                    parse_url = urlparse(row[1])
                    file_name = os.path.basename(parse_url.path)

                    uid = uuid.uuid4()
                    uploaded_name = (
                        "%s/%s/%s-%s" % (settings.MEDIA_DIR, 'img', uid, file_name)
                    ).lower()

                    save_filename = (
                        "%s-%s" % (uid, file_name)
                    ).lower()

                    logo_url = settings.SERVER_URL+'api/view-org-logo/'+save_filename

                    Organization.objects.create(
                        name=row[0],
                        hostname=row[2],
                        logo=logo_url,
                        address=row[3],
                        city=row[4],
                        state=row[5],
                        phone_no=row[6],
                    )

                    response = requests. get(row[1])
                    file = open(uploaded_name, "wb")
                    file. write(response. content)
                    file. close()


