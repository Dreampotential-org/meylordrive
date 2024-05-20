import time
from utils.chirp import CHIRP
from django.core.management.base import BaseCommand
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from storage.models import YouTubeVideo, MediA, Channel

import uuid
from pytube import YouTube
from utils.browser import init_driver



def get_content(ui):
    directory = str(uuid.uuid4())

    CHIRP.info("Here is ui: %s" % ui)
    yt = YouTube(ui)
    yt.streams.filter(
        progressive=True, file_extension='mp4'
    ).order_by('resolution').desc().first().download(
        output_path="/data/meylordrive-youtube-videos/", filename=directory
    )

    file_name =  "/data/meylordrive-youtube-videos/%s" % directory

    print("file_name %s" % file_name)
    # os.system("ffmpeg -i %s %s.mp3" % (file_name, file_name))
    mediA = MediA()
    mediA.path = "/data/meylordrive-youtube-videos/%s.mp4" % directory
    print(mediA.path)

    mediA.name = yt.title

    mediA.save()
    return mediA


def parse_video_url(driver, video_url, channel):
    # Open the video URL
    print("Getting %s" % video_url)
    driver.get(f"https://www.youtube.com/watch?v={video_url}")

    # Wait for the title using WebDriverWait
    title_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="title"]/h1/yt-formatted-string'))
    )

    # Wait for the description using WebDriverWait
    description_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="attributed-snippet-text"]/span/span'))
    )

    # Save video data to the database
    ytv = YouTubeVideo()
    ytv.channel = channel
    ytv.title = title_element.text
    ytv.url = f"https://www.youtube.com/watch?v={video_url}"
    ytv.description = description_element.text
    ytv.save()

    CHIRP.info("creating %s %s"
               % (title_element.text, description_element.text))

    ytv.mediA = get_content(
        f"https://www.youtube.com/watch?v={video_url}"
    )
    ytv.save()



def get_channel(driver, channel):
    youtube_url = 'https://www.youtube.com/' + channel.name + '/videos'
    driver.get(youtube_url)

    # XXX
    # channel.title = 
    channel.url = youtube_url
    # channel.desciption = 
    # number of vidoes
    # channel.videos = 

    channel.save()

    # Use regular expressions to find all video URLs
    while True:
        page_source = driver.page_source
        video_urls = re.findall(r'href="/watch\?v=([a-zA-Z0-9_-]+)"',
                                page_source)


        # XXX Fixme we need to keep paging down getting more videos
        # not all the videos load right away...

        print("Video urls: %s" % video_urls)
        if video_urls:
            break
        else:
            print("waiting to find videos")
            time.sleep(2)

    # Loop through each video URL
    for video_url in video_urls:
        parse_video_url(driver, video_url, channel)

    self.stdout.write(
        self.style.SUCCESS('YouTube video scraping task completed.'))



class Command(BaseCommand):
    help = 'Run the YouTube video scraping task'

    def handle(self, *args, **options):
        driver = init_driver("firefox")

        name = '@TheSourceChiropractic'

        channel = Channel.objects.filter(name=name).first()
        if not channel:
            channel = Channel()
            channel.name = name

        get_channel(driver, channel)

