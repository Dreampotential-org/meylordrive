import os
from django.core.management.base import BaseCommand
from pytube import YouTube

class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # YouTube video URL
        video_url = 'https://www.youtube.com/watch?v=9emilxOLASM'

        # Specify the desired output path (you can change 'downloads' to any folder name)
        output_path = '/data/meylordrive-youtube-videos'

        # Create the output folder if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Call the function to download the YouTube video
        download_youtube_video(video_url, output_path)

def download_youtube_video(video_url, output_path):
    try:
        # Create a YouTube object
        yt = YouTube(video_url)

        # Get the first stream with progressive and mp4 extension
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        # Download the video to the specified output path
        stream.download(output_path)

        print(f"Video downloaded successfully to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
