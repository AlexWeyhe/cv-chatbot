import os

from pathlib import Path

from dotenv import load_dotenv
from guardrails import GuardrailsAsyncOpenAI

from backend.rag import load_index


PATH_GUARDRAILS = Path(__file__).resolve().parent / "guardrails_config.json"

load_dotenv()

def load_resources():
    client = GuardrailsAsyncOpenAI(config=PATH_GUARDRAILS,
                                   raise_guardrail_errors=True,
                                   api_key=os.getenv("OPENAI_API_KEY"))
    
    index = load_index(api_key=os.getenv("OPENAI_API_KEY"))
    retriever = index.as_retriever(similarity_top_k=8)

    return {
        "client": client,
        "retriever": retriever,
    }