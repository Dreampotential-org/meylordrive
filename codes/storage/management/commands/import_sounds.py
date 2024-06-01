import os
import uuid
from django.core.management.base import BaseCommand
from storage.models import MediA
from django.core.files import File

from pytube import YouTube


def create_sound_file(ui):
    directory = str(uuid.uuid4())

    yt = YouTube(ui)
    yt.streams.filter(
        progressive=True, file_extension='mp4'
    ).order_by('resolution').desc().first().download(
        output_path="/data/meylordrive-youtube-videos/", filename=directory
    )
    # video = "/tmp/%s/%s" % (directory, "file")

    file_name =  "/data/meylordrive-youtube-videos/%s" % directory

    os.system("ffmpeg -i %s %s.mp3" % (file_name, file_name))

    sound = MediA()
    # sound.file = File(video)
    sound.path = "/data/meylordrive-youtube-videos/%s.mp3" % directory
    print(sound.path)

    sound.soundfile = True
    sound.name = yt.title
    sound.save()


class Command(BaseCommand):
    help = 'fehdas wst'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # create_sound_file("https://www.youtube.com/watch?v=UZKeLf14-kY")
        # create_sound_file("https://www.youtube.com/watch?v=rJ5sXdtKvjM")
        create_sound_file("https://www.youtube.com/watch?v=h3h035Eyz5A")
