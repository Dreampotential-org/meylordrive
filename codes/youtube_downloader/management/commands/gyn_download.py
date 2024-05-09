# management/commands/your_command_name.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pytube import YouTube
import re

from youtube_downloader.models import YouTubeVideo, YouTubeProfile

class Command(BaseCommand):
    help = 'Run the YouTube video scraping task'

    def add_arguments(self, parser):
        # Add an argument for the YouTube profile name
        parser.add_argument('youtube_profile', type=str, help='Name of the YouTube profile')

    def handle(self, *args, **options):
        try:
            # Create a new instance of the Chrome driver
            driver = webdriver.Chrome()

            # Get the YouTube profile name from command-line arguments
            youtube_profile_name = options['youtube_profile']

            # URL of the YouTube profile page
            youtube_url = f'https://www.youtube.com/{youtube_profile_name}/videos'

            # Open the YouTube profile page
            driver.get(youtube_url)

            # Get the page source
            page_source = driver.page_source

            # Use regular expressions to find all video URLs
            video_urls = re.findall(r'href="/watch\?v=([a-zA-Z0-9_-]+)"', page_source)

            # Get or create the YouTube profile
            youtube_profile, created = YouTubeProfile.objects.get_or_create(profile_name=youtube_profile_name)

            # Loop through each video URL
            for video_url in video_urls[:11]:  # Limit to 5 videos
                try:
                    # Open the video URL
                    driver.get(f"https://www.youtube.com/watch?v={video_url}")

                    # Wait for the title using WebDriverWait
                    title_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="title"]/h1/yt-formatted-string'))
                    )

                    # Wait for the description using WebDriverWait
                    description_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="description"]/yt-formatted-string'))
                    )

                    # Save video data to the database
                    video = YouTubeVideo.objects.create(
                        title=title_element.text,
                        url=f"https://www.youtube.com/watch?v={video_url}",
                        description=description_element.text
                    )
                    video.save()

                    # Associate the video with the YouTube profile
                    youtube_profile.videos.add(video)

                    # Download the video using pytube
                    yt = YouTube(video.url)
                    stream = yt.streams.filter(file_extension='mp4', res='720p').first()
                    stream.download()

                except Exception as e:
                    print(f"Error processing video URL https://www.youtube.com/watch?v={video_url}: {str(e)}")

        finally:
            # Close the browser window after the task is done
            driver.quit()

        self.stdout.write(self.style.SUCCESS('YouTube video scraping task completed.'))
