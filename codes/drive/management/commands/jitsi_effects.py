import time
import os
from django.core.management.base import BaseCommand

from utils.browser import init_driver



class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("here is the start")
        driver = init_driver("firefox")
        driver.get('https://live.realtorstat.com/meeting')

        # login meeting
        # parse events in meeting
        # while True:
        #    parse_event = driver.find_element()..
        #    if parse_event == 'join':
        #    from playsound import playsound
        #    playsound("breath.wav")
        #    if parse_event == 'leave':


