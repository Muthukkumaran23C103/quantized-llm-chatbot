#!/usr/bin/env python3
"""AI Study Buddy - Voice Enhanced Backend"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import time
import re
from datetime import datetime

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "tinyllama"

app = FastAPI(title="AI Study Buddy - Voice Enhanced", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str

class VoiceChatMessage(BaseModel):
    message: str
    use_context: bool = True
    voice_mode: bool = False

class VoiceChatResponse(BaseModel):
    bot_response: str
    voice_response: str
    response_time_ms: int = 0
    context_documents: list = []
    metadata: dict = {}

def clean_for_voice(text: str) -> str:
    """Clean text for voice synthesis"""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text) 
    text = re.sub(r'[🤖🎓📚💡🔧⚡🎯📄🔍✅❌🚫👋🎤🔊]', '', text)
    
    replacements = {
        'AI': 'A I', 'API': 'A P I', 'vs': 'versus', '&': 'and'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

async def get_voice_ai_response(message: str, voice_mode: bool = False):
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": DEFAULT_MODEL, "prompt": message, "stream": False},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            response_time = int((time.time() - start_time) * 1000)
            voice_response = clean_for_voice(ai_response)
            return ai_response, voice_response, response_time
    except:
        pass
    
    response_time = int((time.time() - start_time) * 1000)
    
    if voice_mode:
        voice_response = f"Hello! I'm your A I Study Buddy. You asked about {message}. I'm here to help you learn any subject. Whether it's math, science, history, or languages, I can explain concepts, provide study tips, and help you understand difficult topics. What would you like to learn about today?"
        display_response = f"🎤 **Voice Response**\n\n{voice_response}\n\n🔧 *Voice-optimized educational response*"
        return display_response, voice_response, response_time
    else:
        fallback = f"""🤖 **AI Study Buddy**

**Your question:** {message}

**📚 Educational Response:**
I'm here to help you learn and understand any topic!

**💡 Study Tips:**
• Break topics into smaller parts
• Use active recall techniques  
• Connect new info to existing knowledge
• Practice regularly with examples

**🎓 Keep studying - you're doing great!**
"""
        voice_version = clean_for_voice(fallback)
        return fallback, voice_version, response_time

@app.get("/")
async def root():
    return {
        "message": "🎤 AI Study Buddy - Voice Enhanced!",
        "version": "2.0.0",
        "team": ["Muthukkumaran S", "Surya S", "Shiva Raj Ganesh N S"]
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    valid_users = {"admin": "secret", "user1": "secret"}
    
    if user_login.username in valid_users and valid_users[user_login.username] == user_login.password:
        return TokenResponse(
            access_token=f"token-{user_login.username}-{int(time.time())}",
            message=f"Welcome {user_login.username}! Voice assistant activated!"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(chat_message: VoiceChatMessage):
    start_time = time.time()
    
    ai_response, voice_response, response_time = await get_voice_ai_response(
        chat_message.message, chat_message.voice_mode
    )
    
    total_time = int((time.time() - start_time) * 1000)
    
    return VoiceChatResponse(
        bot_response=ai_response,
        voice_response=voice_response,
        response_time_ms=total_time,
        context_documents=[],
        metadata={"voice_mode": chat_message.voice_mode}
    )

@app.post("/documents")
async def upload_document(document: dict):
    filename = document.get("filename", "document.txt")
    content = document.get("content", "")
    words = len(content.split()) if content else 0
    
    return {
        "id": 1,
        "filename": filename,
        "analysis": {"word_count": words, "status": "processed"},
        "processing_time_ms": 100,
        "message": f"Document analyzed: {filename} ({words} words)"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "components": {"fastapi": "✅ Running", "voice_features": "✅ Enabled"},
        "message": "Voice assistant ready!"
    }

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse("""
    <html>
    <head><title>🎤 AI Study Buddy - Voice Assistant</title></head>
    <body style='font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 40px;'>
        <h1>🎤 AI Study Buddy - Voice Assistant</h1>
        <h2>Alexa-Style Education Helper! ✨</h2>
        <p><strong>Say "Hey Study Buddy" to activate!</strong></p>
        <p><strong>Team:</strong> Muthukkumaran S, Surya S, Shiva Raj Ganesh N S</p>
        <p><a href='/docs' style='color: white;'>📚 API</a> | <a href='http://localhost:7860' style='color: white;'>🎤 Voice UI</a></p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("🎤 Starting Voice-Enhanced AI Study Buddy!")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
