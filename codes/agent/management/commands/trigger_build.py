from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        req = requests.post("http://localhost:8000/api/pipeline/1/")
        print(req.json())
