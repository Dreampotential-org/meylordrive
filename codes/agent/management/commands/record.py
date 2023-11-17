from django.core.management.base import BaseCommand
import requests
from utils.us_states import states
import sys, getopt, time, subprocess, shlex

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from xvfbwrapper import Xvfb
from selenium.webdriver.chrome.service import Service

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import File_3_1

from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()


def set_up():
    global browser
    global xvfb

    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
    )
    print(browser.title)

def login_realtorstat():
    global info
    global browser
    global xvfb
    global platforms
    browser.get("https://live.realtorstat.com/meeting")



def netflix_login():
    global info
    global browser
    global xvfb
    global platforms
    browser.get(platforms[info['platform']]['login'])
    email_input = browser.find_element_by_name('email')
    pass_input = browser.find_element_by_name('password')
    email_input.send_keys(info['username'])
    pass_input.send_keys(info['pass'])
    pass_input.submit()

def hulu_login():
    global info
    global browser
    global xvfb
    global platforms
    browser.get(platforms[info['platform']]['login'])
    email_input = browser.find_element_by_name('login')
    pass_input = browser.find_element_by_name('password')
    email_input.send_keys(info['username'])
    pass_input.send_keys(info['pass'])
    browser.find_element_by_class_name('login-submit').click()

def netflix_fullscreen():
    global browser
    action = webdriver.common.action_chains.ActionChains(browser)
    action.send_keys('f').perform()

def stream():
    global xvfb
    global info
    ffmpeg_stream = 'ffmpeg -f x11grab -s 1280x720 -r 24 -i :%d+nomouse -c:v libx264 -preset superfast -pix_fmt yuv420p -s 1280x720 -threads 0 -f flv "%s"' % (xvfb.display,
                                                                                                                                                               "/tmp/video3")
    args = shlex.split(ffmpeg_stream)
    p = subprocess.Popen(args)


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        set_up()
        login_realtorstat()
        stream()
        browser.quit()
        xvfb.stop()
