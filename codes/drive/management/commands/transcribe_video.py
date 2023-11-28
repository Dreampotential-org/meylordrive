import subprocess, sys, os, json
import pprint

from datetime import datetime, timedelta

from vosk import Model, KaldiRecognizer
from django.core.management.base import BaseCommand

SAMPLE_RATE = 16000
CHUNK_SIZE = 4000


class Transcriber():
    def __init__(self, model_path):
        self.model = Model(model_path)

    def fmt(self, data):
        data = json.loads(data)

        start = min(r["start"] for r in data.get("result", [{ "start": 0 }]))
        end = max(r["end"] for r in data.get("result", [{ "end": 0 }]))

        return {
            "start": str(timedelta(seconds=start)),
            "end": str(timedelta(seconds=end)),
            "text": data["text"]
        }

    def transcribe(self, filename):
        rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        rec.SetWords(True)

        if not os.path.exists(filename):
            raise FileNotFoundError(filename)

        transcription = []

        ffmpeg_command = [
                "whisper",
                filename,
                "--model",
                "small",
                "--language",
                "English",
            ]

        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE) as process:
            print("completed")

    def add_cc_to_video(self, filename):
        print(filename)


class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        filename = "/data/meylordrive-youtube-videos/RePicture.mp4"
        model_path = "vosk-model-small-en-in-0.4"

        transcriber = Transcriber(model_path)
        transcriber.transcribe(filename)
        transcriber.add_cc_to_video(filename)
