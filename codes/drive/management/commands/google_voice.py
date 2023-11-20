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
        driver.get('https://voice.google.com/u/0/about')
        sign_up_links = driver.find_elements(
            by='css selector', value='.signUpLink')
        sign_up_links[0].click()
        time.sleep(2)
        # Locate the email input field and enter the email
        email_input = driver.find_element(
            by='xpath', value='//*[@id="identifierId"]')
        email_input.send_keys('realtorstat')

        next_button = driver.find_element(
            by='xpath', value='//*[@id="identifierNext"]/div/button/span')
        next_button.click()
        time.sleep(2)

        driver.find_elements(
            by='css selector', value='input').send_keys("AgentStat123!")

        next_button = driver.find_element(
            by='xpath', value='//*[@id="identifierNext"]/div/button/span')
        next_button.click()
        time.sleep(2)

        # Close the browser
        # driver.quit()

