from django.apps import AppConfig


class DappxConfig(AppConfig):
    name = 'xppda'

    def ready(self):
        import xppda.signals