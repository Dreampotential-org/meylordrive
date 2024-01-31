from django.core.management.base import BaseCommand
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from moviepy.editor import AudioFileClip
from rich.console import Console
import os
import re
import shutil
import time
import urllib.request
import requests


class SpotifyDownloader(BaseCommand):
    help = 'Download Spotify tracks or playlists from YouTube'

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
        self.SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.SPOTIPY_CLIENT_ID, client_secret=self.SPOTIPY_CLIENT_SECRET
        )
        self.sp = Spotify(client_credentials_manager=self.client_credentials_manager)
        self.file_exists_action = ""
        self.console = Console()

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            url = self.validate_url(input("Enter a Spotify URL: ").strip())
            if "track" in url:
                songs = [self.get_track_info(url)]
            elif "playlist" in url:
                songs = self.get_playlist_info(url)

            start = time.time()
            downloaded = 0
            tmp_dir = "../music/tmp"

            for i, track_info in enumerate(songs, start=1):
                search_term = f"{track_info['artist_name']} {track_info['track_title']} audio"
                video_link = self.find_youtube(search_term)

                self.console.print(
                    f"[magenta]({i}/{len(songs)})[/magenta] Downloading '[cyan]{track_info['artist_name']} - {track_info['track_title']}[/cyan]'..."
                )
                audio = self.download_yt(video_link)
                if audio:
                    self.set_metadata(track_info, audio)
                    os.replace(audio, f"../music/{os.path.basename(audio)}")
                    self.console.print(
                        "[blue]"
                    )
                    downloaded += 1
                else:
                    print("File exists. Skipping...")

            # Ensure the ../music/tmp directory exists or create it
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

            # Ensure the ../music directory exists or create it
            music_dir = "../music"
            if not os.path.exists(music_dir):
                os.makedirs(music_dir)

            end = time.time()
            print()
            os.chdir(music_dir)
            print(f"Download location: {os.getcwd()}")
            self.console.print(
                f"DOWNLOAD COMPLETED: {downloaded}/{len(songs)} song(s) downloaded".center(
                    70, " "
                ),
                style="on green",
            )
            self.console.print(
                f"Total time taken: {round(end - start)} sec".center(70, " "), style="on white"
            )

        except Exception as e:
            print(f"An error occurred: {e}")

    def validate_url(self, sp_url):
        if re.search(r"^(https?://)?open\.spotify\.com/(playlist|track)/.+$", sp_url):
            return sp_url

        raise ValueError("Invalid Spotify URL")

    def get_track_info(self, track_url):
        res = requests.get(track_url)
        if res.status_code != 200:
            raise ValueError("Invalid Spotify track URL")

        track = self.sp.track(track_url)

        track_metadata = {
            "artist_name": track["artists"][0]["name"],
            "track_title": track["name"],
            "track_number": track["track_number"],
            "album_name": track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "artists": [artist["name"] for artist in track["artists"]],
        }

        if "images" in track["album"] and track["album"]["images"]:
            track_metadata["album_art"] = track["album"]["images"][0]["url"]

        if "external_ids" in track and "isrc" in track["external_ids"]:
            track_metadata["isrc"] = track["external_ids"]["isrc"]

        return track_metadata

    def get_playlist_info(self, sp_playlist):
        res = requests.get(sp_playlist)
        if res.status_code != 200:
            raise ValueError("Invalid Spotify playlist URL")
        pl = self.sp.playlist(sp_playlist)
        if not pl["public"]:
            raise ValueError(
                "Can't download private playlists. Change your playlist's state to public."
            )
        playlist = self.sp.playlist_tracks(sp_playlist)

        tracks = [item["track"] for item in playlist["items"]]
        tracks_info = []
        for track in tracks:
            track_url = f"https://open.spotify.com/track/{track['id']}"
            track_info = self.get_track_info(track_url)
            tracks_info.append(track_info)

        return tracks_info

    def find_youtube(self, query):
        phrase = query.replace(" ", "+")
        search_link = "https://www.youtube.com/results?search_query=" + phrase
        count = 0
        while count < 3:
            try:
                response = urllib.request.urlopen(search_link)
                break
            except:
                count += 1
        else:
            raise ValueError("Please check your internet connection and try again later.")

        search_results = re.findall(r"watch\?v=(\S{11})", response.read().decode())
        first_vid = "https://www.youtube.com/watch?v=" + search_results[0]

        return first_vid

    def prompt_exists_action(self):
        """ask the user what happens if the file being downloaded already exists"""
        if self.file_exists_action == "SA":  # SA == 'Skip All'
            return False
        elif self.file_exists_action == "RA":  # RA == 'Replace All'
            return True

        print("This file already exists.")
        while True:
            resp = (
                input("replace[R] | replace all[RA] | skip[S] | skip all[SA]: ")
                .upper()
                .strip()
            )
            if resp in ("RA", "SA"):
                self.file_exists_action = resp
            if resp in ("R", "RA"):
                return True
            elif resp in ("S", "SA"):
                return False
            print("---Invalid response---")

    def download_yt(self, yt_link):
        """download the video in mp3 format from YouTube"""
        yt = YouTube(yt_link)

        try:
            yt.title = "".join([c for c in yt.title if c not in ['/', '\\', '|', '?', '*', ':', '>', '<', '"']])
        except Exception as e:
            print(f"Error retrieving YouTube title: {e}")
            return None

        # Add print statement for debugging
        print("Trying to retrieve YouTube title for:", yt_link)

        # don't download existing files if the user wants to skip them
        exists = os.path.exists(f"../music/{yt.title}.mp3")
        if exists and not self.prompt_exists_action():
            return None

        # download the music
        video = yt.streams.filter(only_audio=True).first()
        if video is None:
            print("No audio stream found. Skipping...")
            return None

        try:
            vid_file = video.download(output_path="../music/tmp")
            # convert the downloaded video to mp3
            base = os.path.splitext(vid_file)[0]
            audio_file = base + ".mp3"
            mp4_no_frame = AudioFileClip(vid_file)
            mp4_no_frame.write_audiofile(audio_file, logger=None)
            mp4_no_frame.close()
            os.remove(vid_file)
            os.replace(audio_file, f"../music/tmp/{yt.title}.mp3")
            audio_file = f"../music/tmp/{yt.title}.mp3"
            return audio_file
        except Exception as e:
            print(f"Error converting video to mp3: {e}")
            return None

    def set_metadata(self, metadata, file_path):
        """adds metadata to the downloaded mp3 file"""

        mp3file = EasyID3(file_path)

        # add metadata
        mp3file["albumartist"] = metadata["artist_name"]
        mp3file["artist"] = metadata["artists"]
        mp3file["album"] = metadata["album_name"]
        mp3file["title"] = metadata["track_title"]
        mp3file["date"] = metadata["release_date"]
        mp3file["tracknumber"] = str(metadata["track_number"])

        # Check if 'isrc' key is present in metadata
        if "isrc" in metadata:
            mp3file["isrc"] = metadata["isrc"]

        mp3file.save()

        # Check if 'album_art' key is present in metadata
        if "album_art" in metadata:
            # add album cover
            audio = ID3(file_path)
            with urllib.request.urlopen(metadata["album_art"]) as albumart:
                audio["APIC"] = APIC(
                    encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
                )
            audio.save(v2_version=3)


if _name_ == "_main_":
    downloader = SpotifyDownloader()
    downloader.handle()