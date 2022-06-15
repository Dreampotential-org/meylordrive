from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        params = {
            'command': "python codes/manage.py gmaps",
            'repo': "git@github.com:aaronorosen/django-zillow.git",

        }
        req = requests.post("http://localhost:8000/tasks/", json=params)
        print(req.json())
