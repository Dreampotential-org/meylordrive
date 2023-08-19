from django.core.management.base import BaseCommand
import requests
from utils.us_states import states


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        command = 'gmaps'

        commands = [
            "get_redfin_cvs_fails",
        ]
        for state in states.keys():
            for command in commands:
                # todo add meta input here to params
                params = {
                    'command': "sudo su -c 'STATE=\"%s\" COMMAND=\"%s\";  bash scripts/batch.sh'" % (state, command),
                    'repo': "git@gitlab.com:a4496/django-zillow.git",
                }
                print(params)
                req = requests.post(
                    "http://127.0.0.1:8000/tasks/", json=params)
                print(req.status_code)
                print(req.json())
