from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        commands = [
            "king_tax",
            "sonoma_tax",
            "miami_dade_tax",
            "charleston_tax",
            "harris_tax",
            "orange_tax",
            "dallas_tax",
            "lake_tax",
            "san_barnardino_tax",
            "santa_barbara_tax",
            "maricopa_tax",
            "palm_beach_tax",
            "san_francisco_tax",
        ]
        for command in commands:
            params = {
                'command': "sudo su -c 'export COMMAND=\"%s\";  bash scripts/batch.sh'" % command,
                'repo': "git@github.com:aaronorosen/django-zillow.git",

            }
            req = requests.post("https://meylorci-api.dreampotential.org/tasks/", json=params)
            print(req.json())
