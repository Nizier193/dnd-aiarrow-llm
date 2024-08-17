import requests
import time
import os
import sys

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

from source.models.llm.langchain_ru_llms.langchain_yandex import YandexChatModel

import requests
import time
import json

class Yandex_LLM:
    test = os.getenv('TEST')

    def __init__(self, max_tokens: int = None):
        self.max_tokens = max_tokens
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Authorization": f"Api-Key {os.getenv('YANDEX_API_KEY')}",
            "Content-Type": "application/json"
        }

        self.chat_model = self.init_chat_model(max_tokens)

    def api_call(self,
                 prompt: str,
                 max_tokens: int,
                 retries: int = 3,
                 system_prompt: str = None) -> str:
        print(f"[Yandex_LLM] api_call: prompt='{prompt}', max_tokens={max_tokens}")
        if self.test == "True":
            return "DUMMY"
        
        try:
            return self.chat_model.invoke(prompt).content
        except Exception as e:
            print(e)
            return "An error occurred while calling the Yandex LLM API."

    def init_chat_model(self, max_tokens: int = None):
        print(f"[Yandex_LLM] init_chat_model: max_tokens={max_tokens}")
        # TODO: implement this

        model = YandexChatModel(
            catalogue_id=os.getenv('YANDEX_CATALOGUE_ID'),
            api_key=os.getenv('YANDEX_API_KEY'),
            model_name="yandexgpt",
            max_tokens=max_tokens if max_tokens else 1000
        )
        return model

    def check_yandex_availability(self):
        print("[Yandex_LLM] check_yandex_availability")
        if self.test == "True":
            return True

        try:
            # Yandex doesn't have a direct model retrieval endpoint, so we'll make a minimal request
            response = self.api_call("Test", max_tokens=1)
            return True if response and not response.startswith("Error:") else False
        except Exception:
            return False