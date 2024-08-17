import os
import sys

from openai import OpenAI
import time

import httpx

from langchain_openai import ChatOpenAI

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

proxy_url = "http://CKhCxU:v0bAeV@45.145.15.77:8000"

class OpenAI_LLM():
    test = os.getenv('TEST')
    def __init__(self, max_tokens: int = None):
        self.max_tokens = max_tokens

        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            http_client=httpx.Client(proxies={"https://": proxy_url})
        )

    def api_call(self,
                 prompt: str,
                 max_tokens: int,
                 retries: int = 3,
                 system_prompt: str = None) -> str:
        print(f"API Call - Model: gpt-4o, Prompt: {prompt}")
        if self.test == "True":
            return "DUMMY"

        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            result = ChatOpenAI(
                openai_api_key=os.getenv('OPENAI_API_KEY'), 
                model_name="gpt-4o",
                max_tokens=self.max_tokens if self.max_tokens else max_tokens,
                http_client=httpx.Client(proxies={"https://": proxy_url})
            ).invoke(prompt, max_tokens=self.max_tokens if self.max_tokens else max_tokens)

            return result.content
        except Exception as e:
            print(e)
            return "Unable to generate content. Please check OpenAI API status."

    def init_chat_model(self):
        print("Initializing Chat Model - Model: gpt-4o")
        return ChatOpenAI(
            openai_api_key=os.getenv('OPENAI_API_KEY'), 
            model_name="gpt-4o",
            http_client=httpx.Client(proxies={"https://": proxy_url})
        )

    def check_openai_availability(self):
        print("Checking OpenAI Availability - Model: gpt-4o")
        if self.test == "True":
            return True

        try:
            response = self.client.models.retrieve("gpt-4o")
            return True
        except Exception:
            return False