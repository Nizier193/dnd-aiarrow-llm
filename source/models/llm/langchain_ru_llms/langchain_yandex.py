from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel, SimpleChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import run_in_executor

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

import requests
from pydantic import Field
import time

class YandexChatModel(BaseChatModel):
    model_name: str
    max_tokens: int = 5
    base_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    api_key: str
    catalogue_id: str
    temperature: float = 0.6
    model_uri: str = None
    headers: Dict[str, str] = Field(default_factory=dict)  # Add this line

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_uri = f"gpt://{self.catalogue_id}/yandexgpt/latest"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        formatted_messages = self._format_messages(messages)
        
        data = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": self.temperature,
                "maxTokens": self.max_tokens
            },
            "messages": formatted_messages
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            content = result['result']['alternatives'][0]['message']['text']
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            
            time.sleep(0.5)

            return ChatResult(generations=[generation])
        except Exception as e:
            raise ValueError(f"Error calling Yandex API: {str(e)}")

    def _format_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        formatted = []
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted.append({"role": "user", "text": message.content})
            elif isinstance(message, AIMessage):
                formatted.append({"role": "assistant", "text": message.content})
            elif isinstance(message, SystemMessage):
                formatted.append({"role": "system", "text": message.content})
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return formatted

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        last_message = messages[-1]
        tokens = last_message.content[: self.n]

        for token in tokens:
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=token))

            if run_manager:
                # This is optional in newer versions of LangChain
                # The on_llm_new_token will be called automatically
                run_manager.on_llm_new_token(token, chunk=chunk)

            yield chunk

        # Let's add some other information (e.g., response metadata)
        chunk = ChatGenerationChunk(
            message=AIMessageChunk(content="", response_metadata={"time_in_sec": 3})
        )
        if run_manager:
            # This is optional in newer versions of LangChain
            # The on_llm_new_token will be called automatically
            run_manager.on_llm_new_token(token, chunk=chunk)
        yield chunk

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "echoing-chat-model-advanced"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters.

        This information is used by the LangChain callback system, which
        is used for tracing purposes make it possible to monitor LLMs.
        """
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": self.model_name,
        }

