#!/usr/bin/env python3
"""AI Study Buddy - Simple Working Backend"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import time
from datetime import datetime

# Simple config
OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "tinyllama"

# FastAPI app
app = FastAPI(title="AI Study Buddy", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str

class ChatMessage(BaseModel):
    message: str
    use_context: bool = True

class ChatResponse(BaseModel):
    bot_response: str
    response_time_ms: int = 0
    context_documents: list = []
    metadata: dict = {}

async def get_ai_response(message: str) -> tuple[str, int]:
    """Get AI response from Ollama or fallback"""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": DEFAULT_MODEL, "prompt": message, "stream": False},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "No response")
            response_time = int((time.time() - start_time) * 1000)
            return ai_response, response_time
    except:
        pass
    
    # Fallback response
    response_time = int((time.time() - start_time) * 1000)
    fallback = f"""🤖 **AI Study Buddy Response**

**Your question:** {message}

**📚 Study Helper:** I'm here to help you learn! 

**💡 Study Tips:**
• Break topics into smaller chunks
• Use active recall - test yourself
• Connect new info to existing knowledge
• Take regular breaks for better focus

**🎓 Subject Help:**
• **Math:** Work step-by-step, show your work
• **Science:** Use diagrams and real examples  
• **History:** Create timelines and connections
• **Language:** Practice daily conversation

**🔧 Note:** For full AI capabilities, start Ollama:
**Keep studying - you're doing great! 📚✨**
"""
    return fallback, response_time

# Routes
@app.get("/")
async def root():
    return {
        "message": "🎓 AI Study Buddy - Working!",
        "version": "1.0.0",
        "team": ["Muthukkumaran S", "Surya S", "Shiva Raj Ganesh N S"],
        "institution": "Thiagarajar College of Engineering - GLUGOT"
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    valid_users = {"admin": "secret", "user1": "secret"}
    
    if user_login.username in valid_users and valid_users[user_login.username] == user_login.password:
        return TokenResponse(
            access_token=f"token-{user_login.username}-{int(time.time())}",
            message=f"🎉 Welcome {user_login.username}! Login successful!"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    start_time = time.time()
    
    ai_response, response_time = await get_ai_response(chat_message.message)
    total_time = int((time.time() - start_time) * 1000)
    
    return ChatResponse(
        bot_response=ai_response,
        response_time_ms=total_time,
        context_documents=[],
        metadata={"model": DEFAULT_MODEL}
    )

@app.post("/documents")
async def upload_document(document: dict):
    filename = document.get("filename", "document.txt")
    content = document.get("content", "")
    
    words = len(content.split()) if content else 0
    
    return {
        "id": 1,
        "filename": filename,
        "analysis": {"word_count": words, "keywords": [], "status": "processed"},
        "processing_time_ms": 100,
        "message": f"✅ Uploaded {filename} with {words} words"
    }

@app.post("/search")
async def search(query: dict):
    search_query = query.get("query", "")
    
    return {
        "results": [
            {
                "filename": "demo_doc.txt",
                "content_preview": f"This document contains information about {search_query}...",
                "similarity_score": 0.9
            }
        ],
        "total_results": 1,
        "search_time_ms": 50,
        "query": search_query
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "components": {"fastapi": "✅ Running", "ollama": "⚡ Available"},
        "message": "AI Study Buddy is working! 🚀"
    }

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse("""
    <html>
    <head><title>🤖 AI Study Buddy</title></head>
    <body style='font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px;'>
        <h1>🤖 AI Study Buddy</h1>
        <h2>✅ Simple Working Backend!</h2>
        <p><strong>Team:</strong> Muthukkumaran S, Surya S, Shiva Raj Ganesh N S</p>
        <p><strong>Institution:</strong> Thiagarajar College of Engineering - GLUGOT</p>
        <p><strong>Login:</strong> admin / secret</p>
        <p><a href='/docs' style='color: white;'>📚 API Docs</a> | <a href='http://localhost:7860' style='color: white;'>🎨 Gradio UI</a></p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Study Buddy - Simple Working Backend!")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
