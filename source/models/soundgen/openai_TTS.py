import sys
import os
import base64
from openai import OpenAI

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

import httpx
proxy_url = os.getenv('OPENAI_PROXY')

class Voices:
    alloy = "alloy"
    echo = "echo"
    fable = "fable"
    onyx = "onyx"
    nova = "nova"
    shimmer = "shimmer"

class OpenAI_TTS():
    test = os.getenv('TEST')
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            http_client=httpx.Client(proxies={"https://": proxy_url})
        )

    def get_available_voices(self):
        return [Voices.alloy, Voices.echo, Voices.fable, Voices.onyx, Voices.nova, Voices.shimmer]

    def api_call(
            self,
            voice: Voices | str,
            speech: str,
            path: str):
        
        if self.test == "True":
            return 'testpath', None

        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=speech
            )
            with open(path, 'wb') as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)

            base_64_audio = base64.b64encode(open(path, 'rb').read()).decode('utf-8')

            return path, base_64_audio
        except Exception as e:
            return None, None

    def check_availability(self):
        if self.test == "True":
            return True

        try:
            response = self.client.models.retrieve('tts-1')
            return True
        except Exception:
            return False