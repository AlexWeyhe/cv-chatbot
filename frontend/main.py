import os
import time
import requests

import streamlit as st
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def start_session():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {
                "role": "assistant",
                "content": "Hi! I'm Alex's CV assistant. Ask me about his professional experience, technical skills, projects, or academic background. I'll provide answers based on his CV and supporting documents."
            }
        ]
    
    if "chat_limit" not in st.session_state:
        st.session_state["chat_limit"] = 0


def stream_answer(answer):
    for word in answer.split(" "):
        yield word + " "
        time.sleep(0.04)


def app():
    st.markdown(
    """
    <div class="header">
        <div>
            <h1>Alexander Weyhe</h1>
            <p>NLP & LLM Enthusiast</p>
        </div>
        <div class="links">
            <a href="https://github.com/AlexWeyhe/cv-chatbot" target="_blank">GitHub</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


    start_session()
    
    for message in st.session_state["chat_history"]:
        avatar_path = "extras/avatar.png" if message["role"] == "assistant" else None
        
        with st.chat_message(message["role"], avatar=avatar_path):
            st.markdown(message["content"])
    
    query = st.chat_input("Ask here...",
                            disabled=st.session_state["chat_limit"] >= 10)
        
    if query:
        with st.chat_message("user"):
            st.markdown(query)

        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": query,
                "chat_history": st.session_state["chat_history"]
                }
        )
        
        answer = response.json()["answer"]
            
        with st.chat_message("assistant", avatar="extras/avatar.png"):
            st.write_stream(stream_answer(answer))
            
        st.session_state["chat_limit"] += 1
        
        st.session_state["chat_history"].extend(
            [
                {
                    "role": "user",
                    "content": query,
                },
                {
                    "role": "assistant",
                    "content": answer,
                }
            ]
        )

    if st.session_state["chat_limit"] >= 10:
        st.info("You reached the limit of 10 questions. Feel free to reach out to me, for further questions.")


if __name__ == "__main__":
    app()
