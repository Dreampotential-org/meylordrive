from django.core.management.base import BaseCommand

from tasks.models import Task, Server


def run_job(server, task):
    print("Run job server: %s %s" % (task, server))


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        # parser.add_argument('is_local', type=str)
        pass

    def handle(self, *args, **options):
        print("Start...")
        tasks = Task.objects.filter(status='not-active')
        print("Number of tasks to run: %s" % len(tasks))

        for task in tasks:
            print(task)
            server = Server.objects.filter(active=False).first()
            run_job(server, task)
