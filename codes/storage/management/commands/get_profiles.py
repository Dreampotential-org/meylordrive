import re
import time
from utils.chirp import CHIRP
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from storage.models import Channel

from utils.browser import init_driver


from storage.management.commands.gym_vedio_download import get_channel



class Command(BaseCommand):
    help = 'Run the YouTube video scraping task'

    def handle(self, *args, **options):
        driver = init_driver("firefox")


        driver.get("https://www.favoree.io/search?category=all&country=all&name=all&min=0&max=0&rating=0&order=highest&language=English&allTopics=all&subTopic=all&rankingRatingMoodDef=all&platform=all&tag=all&duration=all&subscriber=10000000-1000000000")

        time.sleep(5)
        # XXX make this loop for all pages...
        ee = driver.find_elements_by_css_selector(".card-body a h3")
        print("Nnumber of channels: %s" % len(ee))

        Channel.objects.filter().delete()
        for e in ee:
            print(e.text)
            if ("-" in e.text):
                continue
            channel = Channel.objects.filter(name=e.text).first()
            if not channel:
                channel = Channel()
                channel.name = '@%s' % re.sub(" ", "", e.text)
                channel.save()
            get_channel(driver, channel)
