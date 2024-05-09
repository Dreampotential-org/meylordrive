from utils.chirp import CHIRP
from django.core.management.base import BaseCommand
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from storage.models import YouTubeVideo
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
    # video = "/tmp/%s/%s" % (directory, "file")

    file_name =  "/data/meylordrive-youtube-videos/%s" % directory

    print("file_name %s" % file_name)
    # os.system("ffmpeg -i %s %s.mp3" % (file_name, file_name))

    sound = MediA()
    # sound.file = File(video)
    sound.path = "/data/meylordrive-youtube-videos/%s.mp4" % directory
    print(sound.path)

    sound.name = yt.title
    sound.save()


def parse_video_url(driver, video_url):
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
    YouTubeVideo.objects.create(
        title=title_element.text,
        url=f"https://www.youtube.com/watch?v={video_url}",
        description=description_element.text
    )
    CHIRP.info("creating %s %s"
               % (title_element.text, description_element.text))

    get_content(
        f"https://www.youtube.com/watch?v={video_url}"
    )



class Command(BaseCommand):
    help = 'Run the YouTube video scraping task'

    def handle(self, *args, **options):
        driver = init_driver("firefox")
        youtube_url = 'https://www.youtube.com/@TheSourceChiropractic/videos'
        driver.get(youtube_url)
        page_source = driver.page_source

        # Use regular expressions to find all video URLs
        video_urls = re.findall(r'href="/watch\?v=([a-zA-Z0-9_-]+)"',
                                page_source)

        print("Video urls: %s" % video_urls)
        # Loop through each video URL
        for video_url in video_urls[:10]:
            parse_video_url(driver, video_url)

        self.stdout.write(
            self.style.SUCCESS('YouTube video scraping task completed.'))
