
from gigachat import GigaChat as GC
from langchain.chat_models.gigachat import GigaChat
import time

import os
import sys

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

class GigaChat_LLM():
    test = os.getenv('TEST')

    def __init__(self, max_tokens: int = None):
        self.max_tokens = max_tokens

        self.client = GC(credentials=os.getenv('GIGACHAT_API_KEY'), verify_ssl_certs=False)

    def api_call(self,
                 prompt: str,
                 max_tokens: int,
                 retries: int = 3,
                 system_prompt: str = None) -> str:
        if self.test:
            return "DUMMY"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(retries):
            try:
                response = self.client.chat(
                    messages=messages,
                    max_tokens=self.max_tokens if self.max_tokens else max_tokens
                )
                if not response.choices:
                    raise ValueError("No response choices returned")
                return response.choices[0].message.content
            except Exception as e:
                if attempt == retries - 1:
                    return f"Error: Unable to generate content. Please check GigaChat API status."
                time.sleep(2 ** attempt)  # Exponential backoff

    def init_chat_model(self):
        return GigaChat(
            credentials=os.getenv('GIGACHAT_API_KEY'), 
            verify_ssl_certs=False,
            max_tokens=1000
        )

    def check_gigachat_availability(self):
        if self.test:
            return True

        try:
            # GigaChat не имеет прямого метода для проверки доступности модели
            # Вместо этого мы попробуем сделать простой запрос
            response = self.client.chat(messages=[{"role": "user", "content": "Hello"}])
            return True
        except Exception:
            return False