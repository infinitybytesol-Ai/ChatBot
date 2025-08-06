from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # <-- CORS Middleware
import os
from dotenv import load_dotenv
from utils import load_pdf_text, find_relevant_chunks
import requests

load_dotenv()
app = FastAPI()

# Enable CORS (Allow frontend to access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- Allow all origins (change to specific domain in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment & PDF Loading
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PDF_PATH = "DATA.pdf"
pdf_text = load_pdf_text(PDF_PATH)

# Bot Static Info
BOT_INFO = {
    "office": "InfinityByte Stars",
    "email": "info@infinitybyte.com",
    "phone": "+92 300 1234567",
    "address": "InfinityByte Stars, Cant Lahore, Pakistan"
}

# Request Model
class ChatRequest(BaseModel):
    message: str

# Groq API Call
def query_groq_llama(user_input, context):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional assistant for InfinityByte Stars. "
                    "Answer concisely, directly, and only from the given context. "
                    "Do not add extra explanations or greetings."
                )
            },
            {"role": "system", "content": f"Context:\n{context}"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.2
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# Main Chat Endpoint
@app.post("/chat/")
def chat_endpoint(data: ChatRequest):
    user_input = data.message.lower()

    # Handle Greetings
    greetings = ["hi", "hello", "hey", "salam", "assalamualaikum"]
    if any(greet in user_input for greet in greetings):
        return {"response": "👋 Hello! I'm InfinityByte Stars assistant. How can I help you today?"}

    # Handle Farewells
    farewells = ["thank you", "thanks", "goodbye", "bye", "see you"]
    if any(farewell in user_input for farewell in farewells):
        return {"response": "🙏 You're welcome! If you need further assistance, feel free to reach out. Goodbye!"}

    # Handle General Info Queries
    if "office" in user_input or "name" in user_input:
        return {"response": f"🏢 Office: {BOT_INFO['office']}"}
    if "email" in user_input:
        return {"response": f"📧 Email: {BOT_INFO['email']}"}
    if "phone" in user_input or "contact" in user_input:
        return {"response": f"📞 Contact: {BOT_INFO['phone']}"}
    if "address" in user_input or "location" in user_input:
        return {"response": f"📍 Address: {BOT_INFO['address']}"}

    # Default - Query Groq with PDF context
    context = find_relevant_chunks(pdf_text, data.message)
    reply = query_groq_llama(data.message, context)
    return {"response": reply}
