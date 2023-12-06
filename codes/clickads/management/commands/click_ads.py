import time
import os
from django.core.management.base import BaseCommand
from selenium.webdriver.common.keys import Keys

from utils.browser import init_driver


def parse_page(driver, google_targets):
    # now lets parse the results
    results = driver.find_elements(
        by='xpath', value='//*[contains(text(), "Sponsored")]')
    for result in results:
        next_sibling = driver.execute_script(
            "return arguments[0].nextElementSibling",
            result)

        google_click = next_sibling.find_element(
            value="a", by='css selector'
        )

        print(google_click.text)

        title = next_sibling.find_element(
            value="a div span", by='css selector'
        ).text

        print(title)
        for google_target in google_targets:
            if google_target in title.lower():
                print("FOUD")
                google_click.click()
                google_click = GoogleClick()
                google_click.co = google_co
                google_click.target = google_target
                google_click.save()
                return


    driver.find_element(
        by='xpath', value='//*[contains(text(), "More results")]').click()



def go_do_google_co(driver, google_co, google_targets):
    driver.get('https://google.com')
    driver.find_element(by='css selector', value="textarea").send_keys(
        google_co.search_term
    )

    driver.find_element(by='css selector',
                        value="textarea").send_keys(Keys.ENTER)

    while True:
        time.sleep(4)
        parse_page(driver, google_co, google_targets)


class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        driver = init_driver("firefox")
        google_cos = GoogleCo.objects.filter()
        google_targets = GoogleTarget.objects.filter()

        for google_co in google_cos:
            go_do_google_co(driver, google_co, google_targets)
