from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel, SimpleChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import run_in_executor

from gigachat import GigaChat as GC
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from typing import Any, Dict, List, Optional
import time

class GigaChatModel(BaseChatModel):
    client: GC
    max_tokens: Optional[int] = None
    retries: int = 3

    def __init__(self, credentials: str, verify_ssl_certs: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.client = GC(credentials=credentials, verify_ssl_certs=verify_ssl_certs)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        formatted_messages = self._format_messages(messages)
        
        for attempt in range(self.retries):
            try:
                response = self.client.chat(
                    messages=formatted_messages,
                    max_tokens=self.max_tokens
                )
                if not response.choices:
                    raise ValueError("No response choices returned")
                
                content = response.choices[0].message.content
                message = AIMessage(content=content)
                generation = ChatGeneration(message=message)
                
                return ChatResult(generations=[generation])
            except Exception as e:
                if attempt == self.retries - 1:
                    raise ValueError(f"Error: Unable to generate content. Please check GigaChat API status. {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def _format_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        formatted = []
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                formatted.append({"role": "system", "content": message.content})
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return formatted

    @property
    def _llm_type(self) -> str:
        return "gigachat"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"max_tokens": self.max_tokens}

    # The _stream method is not implemented as requested