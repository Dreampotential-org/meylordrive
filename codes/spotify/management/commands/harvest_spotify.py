from django.db import models

from django.core.management.base import BaseCommand
from utils.browser import init_driver


class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        driver = init_driver("firefox")
        driver.get("https://spotify.com")
