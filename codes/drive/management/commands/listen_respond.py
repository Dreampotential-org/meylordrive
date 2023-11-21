import selenium
import time
import os
from django.core.management.base import BaseCommand
# from selenium.webdriver.common.by import by
from utils.browser import init_driver

import pyttsx3
import whisper
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import random
import string
import soundfile as sf
from pydub import AudioSegment
from whisper_mic.whisper_mic import WhisperMic




def save_text_to_speech(text, speaker=None):

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = SpeechT5Processor.from_pretrained(
        "microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained(
        "microsoft/speecht5_tts").to(device)
    vocoder = SpeechT5HifiGan.from_pretrained(
        "microsoft/speecht5_hifigan").to(device)
    embeddings_dataset = load_dataset(
        "Matthijs/cmu-arctic-xvectors", split="validation")


    inputs = processor(text=text, return_tensors="pt").to(device)
    if speaker is not None:
        speaker_embeddings = torch.tensor(
            embeddings_dataset[speaker]["xvector"]
        ).unsqueeze(0).to(device)
    else:
        speaker_embeddings = torch.randn((1, 512)).to(device)
    speech = model.generate_speech(
        inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    if speaker is not None:
        output_filename = f"{speaker}-{'-'.join(text.split()[:6])}.mp3"
    else:
        random_str = ''.join(random.sample(string.ascii_letters+string.digits, k=5))
        output_filename = f"{random_str}-{'-'.join(text.split()[:6])}.mp3"
    sf.write(output_filename, speech.cpu().numpy(),
             samplerate=16000)
    return output_filename



def other():
    model = whisper.load_model("base")
    result = model.transcribe('AgentStat.m4a')
    txt = result["text"]

    print(txt)

    speakers = {
        'awb': 0,     # Scottish male
        'bdl': 1138,  # US male
        'clb': 2271,  # US female
        'jmk': 3403,  # Canadian male
        'ksp': 4535,  # Indian male
        'rms': 5667,  # US male
        'slt': 6799   # US female
    }
    soundfile = None
    for speaker_name, speaker in speakers.items():
        for word in txt.split(" "):
            output_filename = save_text_to_speech(word, speaker)
            print(f"Saved {output_filename}")
            if not soundfile:
                soundfile = AudioSegment(output_filename)
            else:
                soundfile += AudioSegment(output_filename)

    # export sound file
    soundfile.export("output.mp3", format="mp3")


def do_mic_work():
    mic = WhisperMic()
    while True:
        print("Mick listen")
        result = mic.listen()
        print("Mick rsponse: %s" % result)


class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        do_mic_work()
