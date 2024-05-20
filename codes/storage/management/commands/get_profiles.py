from utils.chirp import CHIRP
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from storage.models import Channel

from utils.browser import init_driver



class Command(BaseCommand):
    help = 'Run the YouTube video scraping task'

    def handle(self, *args, **options):
        driver = init_driver("firefox")


        driver.get("https://www.favoree.io/search?category=all&country=all&name=all&min=0&max=0&rating=0&order=highest&language=English&allTopics=all&subTopic=all&rankingRatingMoodDef=all&platform=all&tag=all&duration=all&subscriber=10000000-1000000000")

        # XXX make this loop for all pages...
        ee = driver.find_elements_by_css_selector(".card-body a h3")
        for e in ee:
            channel = Channel.objects.filter(name=e.text).first()
            if not channel:
                channel = Channel()
                channel.name = name
                channel.save()
