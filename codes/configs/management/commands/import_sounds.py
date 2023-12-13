import uuid
from django.core.management.base import BaseCommand
from configs.models import MediA
from django.core.files import File

from pytube import YouTube


def create_sound_file():
    directory = str(uuid.uuid4())

    yt = YouTube(
        "https://www.youtube.com/watch?v=UZKeLf14-kY"
    )
    yt.streams.filter(
        progressive=True, file_extension='mp4'
    ).order_by('resolution').desc().first().download(
        output_path="/tmp/", filename=directory
    )
    # video = "/tmp/%s/%s" % (directory, "file")
    sound = MediA()
    # sound.file = File(video)
    sound.path = "/tmp/%s" % directory
    print(sound.path)
    sound.name = yt.title
    sound.save()


class Command(BaseCommand):
    help = 'fetch and parse iwlist'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_sound_file()
