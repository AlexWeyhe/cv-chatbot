from pathlib import Path

import chromadb
from openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding

from backend.analytics import record_query


INDEX_DIR = Path(__file__).resolve().parents[1] / "index_storage"


SYSTEM_MESSAGE = """You are a CV chatbot for Alexander Weyhe.
        
        You will receive retrieved context from a knowledge base.
        
        Instructions:
        -Answer in the language of the question asked.
        -Answer only using information contained in the retrieved context.
        -If the context is insufficient, do not fabricate an answer. Instead, respond naturally and vary your wording. Avoid repeating the same standard phrase every time.
        -When the requested information is unavailable, use a short, natural, and occasionally playful response appropriate to the question. For example, in German: "Diese Frage beantwortet Alex gerne persönlich.", "Diese Info liegt mir im Moment nicht vor.", "Danke für deine Frage, im Moment kann ich sie leider nicht beantworten.", "Du bist ganz schön neugierig – das weiß ich leider nicht.", "Dieses Detail ist mir nicht bekannt.", "Gute Frage, die Info habe ich gerade nicht parat.", or "Das weiß ich leider nicht."
        -In English, use equivalent natural and varied formulations, for example: "Alex would be happy to answer that personally.", "I don't have that information at the moment.", "Thanks for your question, unfortunately I can't answer that right now.", "You're quite curious – I don't know that one.", "I'm not aware of that detail.", "Good question, I don't have that information at hand.", or "Unfortunately, I don't know."
        -Choose the response that fits the tone and context of the question. Keep it concise, do not invent information and directly answer the question.
        -For company-specific questions: If someone asks about why work for their company, answer "Alex would be happy to answer that personally.".
        
        Answer the user's question using only the retrieved context below. 
        Also consider the message history to determine if a question refers to a previously answered question.
        
        Retrieved context:
        {context}"""


def load_index(api_key):
    embedder = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=api_key,
    )

    db = chromadb.PersistentClient(path=INDEX_DIR)

    chroma_collection = db.get_collection("cv_bot_index")
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        storage_context=storage_context,
        embed_model=embedder,
    )
    
    return index


def answer_question(query: str, 
                    client: OpenAI, 
                    chat_history: list[dict], 
                    retriever,
                    database_url: str | None = None):

    nodes = retriever.retrieve(query)
    context = "\n\n".join([node.get_content() for node in nodes])
    
    messages = [
        {
            "role": "developer", 
            "content": SYSTEM_MESSAGE.format(context=context),
        },
        *chat_history,
        {
            "role": "user",
            "content": query,
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    answer = response.choices[0].message.content

    record_query(
        query=query,
        retrieved_chunks=[
            {
                "rank": rank,
                "content": node.get_content(),
                "metadata": node.metadata,
            }
            for rank, node in enumerate(nodes, start=1)
        ],
        answer=answer or "",
        database_url=database_url,
    )

    return answer
