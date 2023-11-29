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

        AMOUNT = 12
        ProjectCommand.objects.filter().delete()
        ProjectService.objects.filter().delete()
        Domain.objects.filter().delete()
        Server.objects.filter().delete()

        username = 'arosen'
        domain = "dreampotential.org"
        nodes = 4
        ips = []
        for i in range(nodes):
            ips.append("%s.%s" % (i, domain))


        for ip in ips:
            server = Server()
            server.ip_address = ip
            server.username = username
            server.save()

        server_group = ServerGroup()
        server_group.name = "prod"
        server_group.save()
        server_group.servers.add(server)
        server_group.save()

        configs = []

        configs.append({
            'domain': '',
            'start': 'sudo COMMAND=score_es scripts/batch.sh',
            'name': 'score_es',
            'repo': 'git@gitlab.com:a4496/django-zillow.git'})


        for state in states:
            configs.append({
                'domain': '',
                'start': 'sudo STATE=%s COMMAND=get_redfin_cvs_fails scripts/batch.sh' % state,
                'name': 'refresh data',
                'repo': 'git@gitlab.com:a4496/django-zillow.git'})

        for i in range(7):
            continue
            configs.append({
                'domain': '',
                 'start': 'sudo COMMAND=get_agent_photos scripts/batch.sh',
                'name': 'get_homes',
                'repo': 'git@gitlab.com:a4496/django-zillow.git'})

            configs.append({
                'domain': '',
                'start': 'sudo COMMAND=get_homes scripts/batch.sh',
                'name': 'get_homes',
                'repo': 'git@gitlab.com:a4496/django-zillow.git'})

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
