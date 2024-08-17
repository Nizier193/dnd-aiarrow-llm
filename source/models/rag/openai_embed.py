from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import os
import sys

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_directory)

from dotenv import load_dotenv
load_dotenv(root_directory + '/.env')

def initialize_rag_openai():
    chromadb_folder = os.path.join(root_directory, 'chromadb')
    
    embedding_model = OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )

    return Chroma(
        embedding_function=embedding_model,
        persist_directory=chromadb_folder,
        collection_metadata={"hnsw:space": "cosine"},
        collection_name="openai_embeddings"
    )