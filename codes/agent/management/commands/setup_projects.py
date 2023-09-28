from django.core.management.base import BaseCommand
from tasks.models import Domain
from tasks.models import ProjectService
from tasks.models import ProjectCommand
from tasks.models import Server
from tasks.models import ServerGroup
from utils.us_states import states


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # we want to think about this model.

        ProjectCommand.objects.filter().delete()
        ProjectService.objects.filter().delete()
        Domain.objects.filter().delete()
        Server.objects.filter().delete()

        ips = [
               'clnode179.clemson.cloudlab.us',
               'clnode139.clemson.cloudlab.us',
               'clnode133.clemson.cloudlab.us',
               ]
        # ips = ['198.22.255.27']


        for ip in ips:
            server = Server()
            server.ip_address = ip
            server.username = "arosen"
            server.save()

        server_group = ServerGroup()
        server_group.name = "prod"
        server_group.save()
        server_group.servers.add(server)
        server_group.save()
        #    configs.append({
        #        'domain': '',
        #        'start': 'bash install-ubuntu.sh; virtualenv -p python3 venv; source venv/bin/activate; pip install -r requirements.txt; STATE=%s python codes/manage.py get_redfin_cvs_fails' % state,
        #        'name': 'django-zillow',
        #        'repo': 'git@gitlab.com:a4496/django-zillow.git'})


        configs = []
        for i in range(10):
            configs.append({
                'domain': '',
                 'start': 'sudo COMMAND=get_redfin_cvs_fails scripts/batch.sh',
                'name': 'sync_data',
                'repo': 'git@gitlab.com:a4496/django-zillow.git'})

        for i in range(10):
            configs.append({
                'domain': '',
                 'start': 'sudo COMMAND=get_homes scripts/batch.sh',
                'name': 'get_homes',
                'repo': 'git@gitlab.com:a4496/django-zillow.git'})


        for i in range(10):
            configs.append({
                'domain': '',
                 'start': 'sudo COMMAND=sync_homes scripts/batch.sh',
                'name': 'sync_homes',
                'repo': 'git@gitlab.com:a4496/django-zillow.git'})



        ps = ProjectService()
        ps.name = "AgentStat services"
        ps.repo = configs[0]['repo']
        ps.save()
        for config in configs:

            print(config)
            # first we create a project service
            ps.repo = config['repo']
            ps.name = config['name']
            ps.server_group = server_group

            pc = ProjectCommand()
            # ps.command = pc
            pc.project_service = ps

            pc.cmd = config['start']
            pc.repo = config['repo']

            pc.save()
