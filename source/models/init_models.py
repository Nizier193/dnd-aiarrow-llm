import sys
import os

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

from source.models.llm.openai_llm import OpenAI_LLM
from source.models.llm.yandex_llm import Yandex_LLM
from source.models.llm.gigachat_llm import GigaChat_LLM

from source.models.soundgen.suno_mgen import Suno_mgen

from source.models.imgen.dalle_imgen import DalleImgen
from source.models.imgen.yandex_imgen import YandexImgen

from source.models.soundgen.openai_TTS import OpenAI_TTS
from source.models.soundgen.elevenlabs_TTS import ElevenLabsTTS

from source.models.rag.openai_embed import RAG_OpenAI
from source.models.rag.ollama_embed import RAG_Ollama

# Set to None to use model's max_tokens
# You can set it to any value to override model's max_tokens
MAX_TOKENS = 5000
# Initializing models
def setup():
    # Модели используют метод api_call, который возвращает text
    match os.getenv('LLM_PROVIDER'):
        case "openai":
            llm = OpenAI_LLM(max_tokens=MAX_TOKENS)
            chat_model = llm.init_chat_model()
        case "yandex":
            llm = Yandex_LLM(max_tokens=MAX_TOKENS)
            chat_model = llm.init_chat_model()
        case "gigachat":
            llm = GigaChat_LLM(max_tokens=MAX_TOKENS)
            chat_model = llm.init_chat_model()
        case _:
            raise Exception("No available LLM.")

    # Инициализация RAG на основе ChromaDB
    match os.getenv('RAG_PROVIDER'):
        case "openai":
            rag = RAG_OpenAI()
        case "ollama":
            rag = RAG_Ollama()
        case _:
            raise Exception("No available RAG.")

    # Модели используют метод api_call, который возвращает filepath и image_url
    match os.getenv('IMGEN_PROVIDER'):
        case "openai":
            # Указать OpenAI API key
            image_model = DalleImgen()
        case "yandex":
            # Указать Yandex API key и catalogue_id
            image_model = YandexImgen()
        case _:
            raise Exception("No available Image Generators.")

    # Модели используют метод api_call, который возвращает filepath и audio_url
    match os.getenv('TTS_PROVIDER'):
        case "openai":
            # Указать OpenAI API key
            tts_model = OpenAI_TTS()
        case "elevenlabs":
            # Указать ElevenLabs API key
            tts_model = ElevenLabsTTS()
        case _:
            raise Exception("No available TTS models.")

    # Модель использует метод api_call, который возвращает filepath и audio_url
    music_model = Suno_mgen()

    return {
        "LLM": llm,
        "CHAT_MODEL": chat_model,
        "MUSIC_MODEL": music_model,
        "IMAGE_MODEL": image_model,
        "RAG": rag,
        "TTS": tts_model
    }

global setup_models
setup_models = setup()

def reload_models():
    global setup_models

    print("Reloading models...")
    print("LLM: ", os.getenv('LLM_PROVIDER'))
    print("RAG: ", os.getenv('RAG_PROVIDER'))
    print("IMGEN: ", os.getenv('IMGEN_PROVIDER'))
    print("TTS: ", os.getenv('TTS_PROVIDER'))
    setup_models = setup()