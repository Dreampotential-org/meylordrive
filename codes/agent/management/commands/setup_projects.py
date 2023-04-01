from django.core.management.base import BaseCommand
from tasks.models import Domain
from tasks.models import ProjectService
from tasks.models import ProjectCommand
from tasks.models import Server
from tasks.models import ServerGroup


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

        server = Server()
        server.ip_address = "localhost"
        server.username = "jj"
        server.save()

        server_group = ServerGroup()
        server_group.name = "useiam"
        server_group.save()
        server_group.servers.add(server)
        server_group.save()

        configs = [
            {'domain': 'useiam.com',
             'start': 'npm install && npm start & ',
             'name': 'useiam-site',
             'repo': 'git@gitlab.com:devs176/useiam-site.git'},

            {'domain': 'prod-api.useiam.com',
             'start': 'bash scripts/start.sh',
             'name': 'useiam-server',
             'repo':  'git@gitlab.com:devs176/useiam-server.git'},

            {'domain': 'm.useiam.com',
             'start': 'bash scripts/start-prod.sh',
             'name': 'useiam',
             'repo': 'git@gitlab.com:devs176/useiam-site.git'},
        ]



        for config in configs:

            print(config)
            # first we create a project service
            ps = ProjectService()
            ps.repo = config['repo']
            ps.name = config['name']
            ps.server_group = server_group

            pc = ProjectCommand()
            ps.command = pc

            pc.cmd = config['start']
            pc.repo = config['repo']

            pc.save()
            ps.save()

            d = Domain()
            d.name = config['domain']
            d.project_service = ps
            d.save()

