import os
from django.apps import AppConfig
import time


class TasksConfig(AppConfig):
    name = 'tasks'
    verbose_name = "My Application"

    def ready(self):
        os.system("eval `ssh-agent -s`")
        os.system("chmod 600 /opt/server-key")
        time.sleep(5)
        os.system("ssh-add")
        os.system("ssh-add /opt/server-key")


