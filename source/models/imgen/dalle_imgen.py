import os
import sys

import requests
from openai import OpenAI

import httpx

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')


proxy_url = "http://CKhCxU:v0bAeV@45.145.15.77:8000"

class DalleImgen():
    test = os.getenv('TEST')

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            http_client=httpx.Client(proxies={"https://": proxy_url})
        )

    def save_to_file(self, url, filepath):
        print(f"[INFO] Saving file from URL: {url} to {filepath}")  # Логирование
        content = requests.get(url).content
        if os.path.exists(filepath):
            os.remove(filepath)

        with open(filepath, 'wb') as file:
            file.write(
                content
            )

    def api_call(self, prompt: str, filepath: str) -> tuple:
        print(f"[INFO] API call to generate image with prompt: '{prompt}'")  # Логирование
        if self.test == "True":
            dummy_image = "https://get.wallhere.com/photo/1920x1200-px-futuristic-1402737.jpg"
            return self.save_to_file(dummy_image, filepath)

        try:
            response = self.client.images.generate(
                model='dall-e-3',
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            self.save_to_file(image_url, filepath)
            return filepath, image_url

        except Exception as e:
            return None, None

    def check_availability(self):
        print("[INFO] Checking availability of the DALL-E model")  # Логирование
        if self.test == "True":
            return True

        try:
            response = self.client.models.retrieve('dall-e-3')
            return True
        except Exception:
            return False