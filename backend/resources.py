import os

from openai import OpenAI
from dotenv import load_dotenv

from backend.rag import load_index


load_dotenv()

def load_resources():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    index = load_index(api_key=os.getenv("OPENAI_API_KEY"))
    retriever = index.as_retriever(similarity_top_k=5)

    return {
        "client": client,
        "retriever": retriever,
    }