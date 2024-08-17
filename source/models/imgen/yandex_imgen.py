import os
import sys
import time

import base64
from io import BytesIO
from PIL import Image

import requests

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(project_root + '/.env')

class YandexImgen():
    test = os.getenv('TEST')

    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.catalogue_id = os.getenv('YANDEX_CATALOGUE_ID')

    def generate_image(self, text):
        print(f"[INFO] YandexImgen: Generating image with prompt: '{text}'")  # Логирование
        prompt = {
            "modelUri": f"art://{self.catalogue_id}/yandex-art/latest",
            "generationOptions": {
                "seed": 17
            },
            "messages": [
                {
                    "weight": 1,
                    "text": text
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"

        headers = {
            'Content-Type': "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }

        response = requests.post(
            url, headers=headers, json=prompt
        ).json()

        return response
    
    def get_base64_image(self, response, wait = 2):
        print(f"[INFO] YandexImgen: Retrieving base64 image with response ID: {response['id']}")  # Логирование
        headers = {
            'Content-Type': "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }
        
        url = f'https://llm.api.cloud.yandex.net:443/operations/{response["id"]}'
        
        while True:
            req = requests.get(url=url, headers=headers).json()
            if req.get('done', False):
                break
            time.sleep(wait)

        return req, url


    def save_image(self, req, filename):
        print(f"[INFO] YandexImgen: Saving image to {filename}")  # Логирование
        base64_string = req["response"]["image"]
        decoded_bytes = base64.b64decode(base64_string)

        image_buffer = BytesIO(decoded_bytes)

        image = Image.open(image_buffer)

        image.save(filename)

        return filename


    def api_call(self, prompt: str, filepath: str) -> tuple:
        print(f"[INFO] YandexImgen: API call to generate image with prompt: '{prompt}'")  # Логирование
        if self.test == "True":
            # Тестовый режим
            dummy_image = "https://get.wallhere.com/photo/1920x1200-px-futuristic-1402737.jpg"
            self.save_to_file(dummy_image, filepath)
            return filepath, dummy_image

        try:
            response = self.generate_image(prompt)
            req, url = self.get_base64_image(response)
            image = self.save_image(req, filepath)
            return image, url
        except Exception as e:
            print(f"Error generating image: {e}")
            return None, None

    def save_to_file(self, url, filepath):
        print(f"[INFO] YandexImgen: Saving file from URL: {url} to {filepath}")  # Логирование
        content = requests.get(url).content
        if os.path.exists(filepath):
            os.remove(filepath)

        with open(filepath, 'wb') as file:
            file.write(content)

    def check_availability(self):
        print("[INFO] YandexImgen: Checking availability of the Yandex API")  # Логирование
        if self.test == "True":
            return True

        try:
            # Проверка доступности API Yandex
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
            headers = {
                "Authorization": f"Api-Key {self.api_key}"
            }
            response = requests.get(url, headers=headers)
            return response.status_code == 200
        except Exception:
            print("[INFO] YandexImgen: Yandex API is not available")  # Логирование
            return False