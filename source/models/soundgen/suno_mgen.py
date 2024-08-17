import os
import sys
import time

from suno import Suno, ModelVersions


root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

import requests

class Suno_mgen:
    def __init__(self):
        self.test = os.getenv('TEST')
        self.dummy_link = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        self.client = Suno(
            cookie=os.getenv('SUNO_COOKIE'),
            model_version=ModelVersions.CHIRP_V3_5
        )

    def save_music(self, url: str, filepath: str) -> str:
        response = requests.get(url)
        response.raise_for_status()

        with open(filepath, 'wb') as file:
            file.write(response.content)

        return filepath

    def generate_song(self, prompt, is_custom=False, tags=None, title=None, make_instrumental=False):
        max_attempts = 5
        try:
            songs = self.client.generate(
                prompt=prompt,
                is_custom=is_custom,
                tags=tags,
                title=title,
                make_instrumental=make_instrumental,
                wait_audio=True,
            )
            return songs
        except Exception as e:
            return "Failed to generate song after multiple attempts"

    def wait_for_generation(self, song_id, max_wait_time=600):
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            status = self.client.get_song_status(song_id)
            if status == 'completed':
                return True
            time.sleep(30)  # Check every 30 seconds

    def download_songs(self, songs):
        downloaded_files = []
        for song in songs:
            file_path = self.client.download(song=song)
            print(f"Song downloaded to: {file_path}")
            downloaded_files.append(file_path)
        return downloaded_files

    def api_call(self, prompt: str, filepath: str) -> str:
        if self.test == "True":
            return self.save_music(self.dummy_link, filepath), self.dummy_link

        try:
            songs = self.generate_song(prompt)
            downloaded_files = self.download_songs(songs)
            if downloaded_files:
                return downloaded_files[0], songs[0].audio_url
            else:
                raise Exception("No songs were downloaded")
        except Exception as e:
            print(f"An error occurred while generating or saving music with Suno. {e}")
            print(f"Using base dummy music.")
            return self.save_music(self.dummy_link, filepath), self.dummy_link