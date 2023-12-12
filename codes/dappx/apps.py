from django.apps import AppConfig


class DappxConfig(AppConfig):
    name = 'dappx'

    def ready(self):
        import dappx.signals