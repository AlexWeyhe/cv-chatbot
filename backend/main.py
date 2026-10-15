from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic import BaseModel

from backend.rag import answer_question
from backend.resources import load_resources


class ChatRequest(BaseModel):
    message: str
    chat_history: list[dict]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.resources = load_resources()
    
    yield
    
    app.state.resources = None


app = FastAPI(lifespan=lifespan)


@app.post("/chat")
def chat(request: Request, body: ChatRequest):
    resources = request.app.state.resources
    
    answer = answer_question(
        query=body.message,
        client=resources["client"],
        chat_history=body.chat_history,
        retriever=resources["retriever"],
    )

    return {"answer": answer}
