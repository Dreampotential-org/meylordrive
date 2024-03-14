# management/commands/your_command_name.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from storage.models import YouTubeVideo
# from models import YouTubeVideo

class Command(BaseCommand):
    help = 'Run the YouTube video scraping task'

    def handle(self, *args, **options):
        try:
            # Create a new instance of the Chrome driver
            driver = webdriver.Chrome()

            # URL of the YouTube profile page
            youtube_url = 'https://www.youtube.com/@TheSourceChiropractic/videos'

            # Open the YouTube profile page
            driver.get(youtube_url)

            # Get the page source
            page_source = driver.page_source

            # Use regular expressions to find all video URLs
            video_urls = re.findall(r'href="/watch\?v=([a-zA-Z0-9_-]+)"', page_source)

            # Loop through each video URL
            for video_url in video_urls[:10]:
                try:
                    # Open the video URL
                    driver.get(f"https://www.youtube.com/watch?v={video_url}")

                    # Wait for the title using WebDriverWait
                    title_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="title"]/h1/yt-formatted-string'))
                    )

                    # Wait for the description using WebDriverWait
                    description_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="attributed-snippet-text"]/span/span'))
                    )

                    # Save video data to the database
                    YouTubeVideo.objects.create(
                        title=title_element.text,
                        url=f"https://www.youtube.com/watch?v={video_url}",
                        description=description_element.text
                    )

                except Exception as e:
                    print(f"Error processing video URL https://www.youtube.com/watch?v={video_url}: {str(e)}")

        finally:
            # Close the browser window after the task is done
            driver.quit()

        self.stdout.write(self.style.SUCCESS('YouTube video scraping task completed.'))
