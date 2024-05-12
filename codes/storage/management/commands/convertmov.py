import os
import uuid

from django.core.management.base import BaseCommand
from storage.models import Upload
from django.core.files import File

from storage.views import convert_file



class Command(BaseCommand):
    help = 'fehdas wst'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        uploads = Upload.objects.filter()
        for upload in uploads:
            if '.mov' in upload.Url.lower():
                converted = convert_file(upload.Url)
                print(converted)
                upload.Url = converted
                upload.save()
            print(upload.id, upload.file)
