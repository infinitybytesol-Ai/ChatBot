from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from utils import load_pdf_text, find_relevant_chunks
import requests

load_dotenv()
app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PDF_PATH = "DATA.pdf"
pdf_text = load_pdf_text(PDF_PATH)

BOT_INFO = {
    "office": "InfinityByte Stars",
    "email": "info@infinitybyte.com",
    "phone": "+92 300 1234567",
    "address": "InfinityByte Stars, Cant Lahore, Pakistan"
}

class ChatRequest(BaseModel):
    message: str

def query_groq_llama(user_input, context):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful InfinityByte Stars assistant. Only use the provided context."},
            {"role": "system", "content": f"Context:\n{context}"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

@app.post("/chat/")
def chat_endpoint(data: ChatRequest):
    user_input = data.message.lower()

    # Check for general info request
    if any(keyword in user_input for keyword in ["office", "name"]):
        return {"response": f"🏢 Office: {BOT_INFO['office']}"}
    if any(keyword in user_input for keyword in ["email"]):
        return {"response": f"📧 Email: {BOT_INFO['email']}"}
    if any(keyword in user_input for keyword in ["phone", "contact"]):
        return {"response": f"📞 Contact: {BOT_INFO['phone']}"}
    if any(keyword in user_input for keyword in ["address", "location"]):
        return {"response": f"📍 Address: {BOT_INFO['address']}"}

    # Default: respond based on PDF + Groq
    context = find_relevant_chunks(pdf_text, data.message)
    reply = query_groq_llama(data.message, context)
    return {"response": reply}
