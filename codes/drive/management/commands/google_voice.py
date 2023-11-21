import selenium
import time
import os
from django.core.management.base import BaseCommand
# from selenium.webdriver.common.by import by
from utils.browser import init_driver



class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("here is the start")
        driver = init_driver("firefox")
        driver.get('https://voice.google.com/u/0/about')

        cookies_path = 'cookies.txt'
        if os.path.exists(cookies_path):
            with open(cookies_path, 'r')as file:             
                cookies=eval(file.read())
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                        print("Added cookie")
                    except selenium.common.exceptions.InvalidCookieDomainException:
                        pass

        driver.get('https://voice.google.com/')

        sign_up_links = driver.find_elements(
            by='css selector', value='.signUpLink')
        if sign_up_links:
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

            driver.find_element(
                by='css selector', value='input[type="password"]'
            ).send_keys("AgentStat123!")

            next_button = driver.find_element(
                by='css selector', value='#passwordNext')
            next_button.click()
            time.sleep(2)
            with open(cookies_path,'w') as file:
                file.write(str(driver.get_cookies()))
        

        while True:
            incoming_call = driver.find_elements(
                by='css selector',
                value=".in-call-status")
            print(len(incoming_call))
            if incoming_call:
                print("in bound call")
                remote_name = driver.find_element(by="css selector", value=".remote-display-name").text
                phone_number = driver.find_element(by="css selector", value=".phone-number").text

                print("%s %s" % (remote_name, phone_number))

                answer_button = driver.find_elements(
                    by='css selector',
                    value=".pickup-call-button-container")

                print(answer_button)
                # answer the call right away
                if answer_button:
                    print("We are answering an incoming call")
                    answer_button[0].click()
            time.sleep(1)
            print("Polling for inbound call event")

            # call-end-button
