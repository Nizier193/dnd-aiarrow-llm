from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

import os
import sys

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

class RAG_Ollama():
    def similarity_search(self, game_uuid: str, query: str, k: int = 3):
        rag = initialize_rag_ollama(game_uuid)
        return rag.similarity_search(query, k)
    
    def add_texts(self, game_uuid: str, text: str):
        rag = initialize_rag_ollama(game_uuid)
        return rag.add_texts(text)

def initialize_rag_ollama(game_uuid: str):
    chromadb_folder = os.path.join(root_directory, 'chromadb')

    embedding_model = OllamaEmbeddings(
        model = os.getenv('OLLAMA_MODEL'),
        base_url = os.getenv('OLLAMA_ENDPOINT')
    )

    return Chroma(
        embedding_function=embedding_model,
        persist_directory=chromadb_folder,
        collection_name=game_uuid
    )