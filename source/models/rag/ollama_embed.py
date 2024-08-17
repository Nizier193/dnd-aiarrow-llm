from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

import os
import sys

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

def initialize_rag_ollama():
    chromadb_folder = os.path.join(root_directory, 'chromadb')

    embedding_model = OllamaEmbeddings(
        model = os.getenv('OLLAMA_MODEL'),
        base_url = os.getenv('OLLAMA_ENDPOINT')
    )

    return Chroma(
        embedding_function=embedding_model,
        persist_directory=chromadb_folder
    )