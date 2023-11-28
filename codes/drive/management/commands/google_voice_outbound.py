from playsound import playsound
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
from utils import google as google_utils
from utils.chirp import CHIRP
from drive.models import Contact




def save_text_to_speech(text, speaker=None):

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = SpeechT5Processor.from_pretrained(
        "microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained(
        "microsoft/speecht5_tts").to(device)
    vocoder = SpeechT5HifiGan.from_pretrained(
        "microsoft/speecht5_hifigan").to(device)
    embeddings_dataset = load_dataset(
        "Matthijs/cmu-arctic-xvectors",
        split="validation")


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
        output_filename = f"{speaker}-{'-'.join(text.split()[:6])}.wav"
    else:
        random_str = ''.join(random.sample(string.ascii_letters+string.digits, k=5))
        output_filename = f"{random_str}-{'-'.join(text.split()[:6])}.wav"
    sf.write(output_filename, speech.cpu().numpy(),
             samplerate=16000)
    print(output_filename)
    return output_filename



def other():
    # model = whisper.load_model("base")
    # result = model.transcribe('AgentStat.m4a')


    model = whisper.load_model("base")
    audio = "/data/dreampotential/django-zillow/AgentStat.m4a"
    result = model.transcribe(audio)

    txt = "Hello let us see if this basic program is changing voices for us thank you thank you."
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
            print("creating word %s as speaker %s" % (txt, speaker))
            output_filename = save_text_to_speech(txt, speaker)
            print(f"Saved {output_filename}")
            if not soundfile:
                soundfile = AudioSegment.from_wav(output_filename)
            else:
                soundfile += AudioSegment.from_wav(output_filename)

    # export sound file
    soundfile.export("output.mp3", format="mp3")
    print("writign sound file")


import pyttsx3
def play_other():
    # initialize Text-to-speech engine
    engine = pyttsx3.init()

    # convert this text to speech
    text = "Python is a great programming language"
    engine.say(text)
    # play the speech
    engine.runAndWait()

    # get details of speaking rate
    rate = engine.getProperty("rate")
    print(rate)

    # setting new voice rate (faster)
    engine.setProperty("rate", 300)
    engine.say(text)
    engine.runAndWait()

    # slower
    engine.setProperty("rate", 100)
    engine.say(text)
    engine.runAndWait()

    # get details of all voices available
    voices = engine.getProperty("voices")
    print(voices)
    # set another voice
    engine.setProperty("voice", voices[1].id)
    engine.say(text)
    engine.runAndWait()

    # saving speech audio into a file
    engine.save_to_file(text, "python.mp3")
    engine.runAndWait()


class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # play_other()
        # other()
        driver = init_driver("firefox")
        contacts = Contact.objects.filter()
        for contact in contacts:
            google_utils.init_google_voice(driver)
            google_utils.send_sms(
                driver, contact, get_message(contact)
            )
            call = google_utils.dial_number(driver, contact)
            google_utils.monitor_call(driver, call)
            # google_utils.answer_call(driver)

        # while True:
