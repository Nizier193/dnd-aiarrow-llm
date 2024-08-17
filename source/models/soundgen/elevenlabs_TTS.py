import os
import sys
from typing import Dict, List

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

from elevenlabs.client import ElevenLabs
from elevenlabs import save, Voice

class ElevenLabsTTS:
    test = os.getenv('TEST')

    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.voices: Dict[str, Voice] = {}
        self._load_voices()

    def _load_voices(self):
        if self.test == "True":
            return

        all_voices = self.client.voices.get_all()
        self.voices = {voice.name: voice for voice in all_voices.voices}

    def get_available_voices(self) -> List[str]:
        return list(self.voices.keys())

    def api_call(
            self,
            voice_name: str,
            speech: str,
            path: str):
        
        if self.test == "True":
            return 'testpath', None

        try:
            voice = self.voices.get(voice_name)
            if not voice:
                raise ValueError(f"Voice '{voice_name}' not found")

            audio = self.client.generate(
                text=speech,
                voice=voice,
                model="eleven_multilingual_v2"
            )
            save(audio, path)

            return path, None
        
        except Exception as e:
            print("Error in generating TTS:", str(e))
            return None, None

    def check_availability(self):
        if self.test == "True":
            return True

        try:
            self._load_voices()
            return len(self.voices) > 0
        except Exception:
            return False
