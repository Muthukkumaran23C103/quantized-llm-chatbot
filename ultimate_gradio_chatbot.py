#!/usr/bin/env python3
"""
Ultimate Quantized LLM Chatbot - Best Version
Real AI interaction + Document upload + Enhanced Voice + Beautiful UI
"""

import gradio as gr
import requests
import json
import time
import logging
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE = "http://localhost:8000"
UPLOAD_DIR = Path("./data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Global state
class UltimateState:
    def __init__(self):
        self.auth_token = None
        self.username = None
        self.conversation_history = []
        self.current_language = "en"
        self.voice_enabled = True
        self.backend_connected = False
        self.uploaded_documents = []
        self.session_stats = {"questions": 0, "docs_uploaded": 0, "searches": 0}

state = UltimateState()

def check_backend_connection() -> bool:
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            state.backend_connected = True
            return True
    except:
        state.backend_connected = False
    return False

def login_user(username: str, password: str) -> str:
    """Enhanced login with backend connection check"""
    if not username or not password:
        return create_status_card("Please enter both username and password to start!", "warning")
    
    try:
        # Check backend first
        if not check_backend_connection():
            return create_status_card(
                """🚫 **Backend Not Connected**
                
Your quantized LLM backend isn't running yet.

**To start the backend:**
```bash
cd /home/zen/quantized-llm-chatbot
python enhanced_backend.py
```

Or if you have the full system:
```bash  
./launch_backend.sh
```

Then refresh and try logging in again! 🔄""", "error")
        
        # Attempt login
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            state.auth_token = data.get("access_token")
            state.username = username
            state.session_stats = {"questions": 0, "docs_uploaded": 0, "searches": 0}
            
            # Get model status
            try:
                model_response = requests.get(f"{API_BASE}/models/status", timeout=5)
                if model_response.status_code == 200:
                    model_info = model_response.json()
                    
                    return f"""
<div class="login-success animate-bounce-in">
    <div class="success-header">
        <div class="success-icon animate-pulse">🎉</div>
        <div class="success-title">Welcome {username}!</div>
        <div class="success-subtitle">Quantized LLM AI Connected</div>
    </div>
    
    <div class="model-status">
        <div class="status-grid">
            <div class="status-item animate-fade-in" style="animation-delay: 0.2s;">
                <div class="status-icon">🤖</div>
                <div class="status-info">
                    <div class="status-label">AI Model</div>
                    <div class="status-value">{'✅ Loaded' if model_info.get('loaded') else '⚠️ Loading...'}</div>
                </div>
            </div>
            
            <div class="status-item animate-fade-in" style="animation-delay: 0.4s;">
                <div class="status-icon">⚡</div>
                <div class="status-info">
                    <div class="status-label">Device</div>
                    <div class="status-value">{model_info.get('device', 'CPU').upper()}</div>
                </div>
            </div>
            
            <div class="status-item animate-fade-in" style="animation-delay: 0.6s;">
                <div class="status-icon">📚</div>
                <div class="status-info">
                    <div class="status-label">Documents</div>
                    <div class="status-value">{model_info.get('documents_count', 0)}</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="welcome-features">
        <div class="feature-item animate-slide-up" style="animation-delay: 0.8s;">
            <span class="feature-icon">🧠</span> Real AI responses from quantized models
        </div>
        <div class="feature-item animate-slide-up" style="animation-delay: 1s;">
            <span class="feature-icon">🎤</span> Enhanced voice with 6 languages
        </div>
        <div class="feature-item animate-slide-up" style="animation-delay: 1.2s;">
            <span class="feature-icon">📄</span> Working document upload & RAG
        </div>
    </div>
    
    <div class="ready-message animate-glow" style="animation-delay: 1.4s;">
        🚀 <strong>Ready for AI interaction!</strong> 🚀
    </div>
</div>
                    """
                
            except Exception as e:
                logger.warning(f"Could not get model status: {e}")
            
            return create_status_card(f"✅ **Welcome {username}!**\n\n🤖 Quantized LLM Connected\n🚀 Ready for AI chat!", "success")
        else:
            return create_status_card("❌ Login failed - Try any username/password for demo", "error")
            
    except Exception as e:
        return create_status_card(f"🚫 Connection Error: {str(e)}", "error")

def create_status_card(message: str, status_type: str) -> str:
    """Create animated status cards"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    colors = {"success": "#4CAF50", "error": "#f44336", "warning": "#ff9800", "info": "#2196F3"}
    
    icon = icons.get(status_type, "ℹ️")
    color = colors.get(status_type, "#2196F3")
    
    return f"""
<div class="status-card {status_type} animate-bounce-in">
    <div class="status-content">
        <div class="status-icon" style="color: {color};">{icon}</div>
        <div class="status-message">{message}</div>
    </div>
</div>
    """

def ultimate_chat_with_ai(message: str, history: List) -> Tuple[List, str, str]:
    """Ultimate chat function with real AI"""
    if not state.auth_token:
        if history is None:
            history = []
        history.append([message, "🔐 **Please log in first to chat with the AI!**"])
        return history, "", ""
    
    if not message.strip():
        return history, "", ""
    
    if history is None:
        history = []
    
    # Update stats
    state.session_stats["questions"] += 1
    
    # Check backend connection
    if not state.backend_connected:
        check_backend_connection()
        if not state.backend_connected:
            error_response = "🚫 **Backend Disconnected**\n\nYour quantized LLM backend isn't responding. Please start it first:\n```bash\npython enhanced_backend.py\n```"
            history.append([message, error_response])
            return history, "", "Backend is not connected. Please start the backend server."
    
    try:
        start_time = time.time()
        
        # Send to real AI backend
        response = requests.post(
            f"{API_BASE}/chat/quantized",
            json={
                "message": message,
                "language": state.current_language,
                "use_context": True,
                "voice_mode": True,
                "max_tokens": 300
            },
            headers={"Authorization": f"Bearer {state.auth_token}"} if state.auth_token else {},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            
            # Enhance response with model info
            inference_time = result.get("inference_time", 0)
            model_loaded = result.get("model_loaded", False)
            
            if model_loaded and inference_time:
                enhanced_response = f"""🤖 **Quantized AI Response** ⚡{inference_time}ms

{ai_response}

💡 **Session Stats:** {state.session_stats["questions"]} questions • {state.session_stats["docs_uploaded"]} docs • {state.session_stats["searches"]} searches"""
            else:
                enhanced_response = ai_response
            
            # Add to conversation  
            history.append([message, enhanced_response])
            
            # Get TTS text
            tts_text = result.get("tts_text", clean_for_tts(ai_response))
            
            return history, "", tts_text
            
        else:
            error_msg = f"❌ **AI Error** (Status {response.status_code})\n\nThe AI model encountered an issue. This might be due to:\n- Model still loading\n- High server load\n- Network timeout\n\nTry asking again in a moment!"
            history.append([message, error_msg])
            return history, "", "Sorry, the AI model is having an issue. Please try again."
            
    except requests.exceptions.Timeout:
        error_msg = "⏱️ **Request Timeout**\n\nThe AI is taking longer than usual to respond. This might be because:\n- Model is processing a complex request\n- Server is under load\n\nTry asking a simpler question or wait a moment!"
        history.append([message, error_msg])
        return history, "", "The AI request timed out. Please try again with a simpler question."
        
    except Exception as e:
        error_msg = f"🚫 **Connection Error**\n\nCouldn't connect to the AI: {str(e)}\n\nMake sure your backend is running:\n```bash\npython enhanced_backend.py\n```"
        history.append([message, error_msg])
        return history, "", "There was a connection error. Please check the backend."

def ultimate_upload_documents(files) -> str:
    """Ultimate document upload with real backend processing"""
    if not state.auth_token:
        return create_upload_status("🔐 Please log in first to upload documents", "warning")
    
    if not files:
        return create_upload_status("📁 No files selected", "info")
    
    if not state.backend_connected:
        check_backend_connection()
        if not state.backend_connected:
            return create_upload_status("🚫 Backend not connected - Please start your backend first", "error")
    
    try:
        processed_files = []
        total_words = 0
        files_list = files if isinstance(files, list) else [files]
        
        for file in files_list:
            if hasattr(file, 'name'):
                filename = file.name
                
                try:
                    # Read file content
                    if hasattr(file, 'read'):
                        content = file.read()
                    else:
                        with open(file, 'rb') as f:
                            content = f.read()
                    
                    # Convert to text
                    if isinstance(content, bytes):
                        try:
                            text_content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            text_content = content.decode('utf-8', errors='ignore')
                    else:
                        text_content = str(content)
                    
                    # Send to backend for processing
                    response = requests.post(
                        f"{API_BASE}/documents",
                        data={
                            "filename": filename,
                            "content": text_content
                        },
                        headers={"Authorization": f"Bearer {state.auth_token}"} if state.auth_token else {},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        processed_files.append({
                            "filename": result.get("filename", filename),
                            "language": result.get("language", "unknown"),
                            "word_count": result.get("word_count", 0),
                            "chunks": result.get("chunks_created", 0),
                            "doc_id": result.get("document_id", "unknown")
                        })
                        total_words += result.get("word_count", 0)
                        
                        # Add to local state
                        state.uploaded_documents.append(result)
                        state.session_stats["docs_uploaded"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
        
        if processed_files:
            return create_upload_success(processed_files, total_words)
        else:
            return create_upload_status("❌ Failed to process any files", "error")
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return create_upload_status(f"❌ Upload failed: {str(e)}", "error")

def create_upload_success(files: List[Dict], total_words: int) -> str:
    """Create beautiful animated upload success message"""
    files_html = ""
    for i, file in enumerate(files):
        files_html += f"""
        <div class="uploaded-file animate-slide-up" style="animation-delay: {i * 0.1}s;">
            <div class="file-icon">📄</div>
            <div class="file-info">
                <div class="file-name">{file['filename']}</div>
                <div class="file-details">
                    📊 {file['word_count']:,} words • 🌍 {file['language']} • 🧩 {file['chunks']} chunks
                </div>
            </div>
            <div class="file-status">✅</div>
        </div>
        """
    
    return f"""
<div class="upload-success animate-bounce-in">
    <div class="success-header">
        <div class="success-icon animate-pulse">🎉</div>
        <div class="success-title">Documents Processed Successfully!</div>
        <div class="success-subtitle">Your files are now available for AI Q&A</div>
    </div>
    
    <div class="upload-stats">
        <div class="stat-item animate-fade-in" style="animation-delay: 0.2s;">
            <div class="stat-number">{len(files)}</div>
            <div class="stat-label">Files</div>
        </div>
        <div class="stat-item animate-fade-in" style="animation-delay: 0.4s;">
            <div class="stat-number">{total_words:,}</div>
            <div class="stat-label">Words</div>
        </div>
        <div class="stat-item animate-fade-in" style="animation-delay: 0.6s;">
            <div class="stat-number">{sum(f['chunks'] for f in files)}</div>
            <div class="stat-label">Chunks</div>
        </div>
    </div>
    
    <div class="uploaded-files">
        {files_html}
    </div>
    
    <div class="upload-tip animate-slide-up" style="animation-delay: 0.8s;">
        💡 <strong>Now you can:</strong> Ask questions about your documents, search for specific information, or request summaries!
    </div>
</div>
    """

def create_upload_status(message: str, status_type: str) -> str:
    """Create upload status message"""
    return create_status_card(message, status_type)

def ultimate_search_documents(query: str) -> str:
    """Ultimate document search with real backend"""
    if not state.auth_token:
        return create_search_status("🔐 Please log in first", "warning")
    
    if not query.strip():
        return create_search_status("🔍 Enter a search query to find information in your documents", "info")
    
    if not state.backend_connected:
        check_backend_connection()
        if not state.backend_connected:
            return create_search_status("🚫 Backend not connected", "error")
    
    # Update stats
    state.session_stats["searches"] += 1
    
    try:
        response = requests.get(
            f"{API_BASE}/search",
            params={"query": query, "limit": 5},
            headers={"Authorization": f"Bearer {state.auth_token}"} if state.auth_token else {},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            total_docs = data.get("total_documents", 0)
            
            if not results:
                return create_search_status(
                    f"""🔍 **No matches found for "{query}"**
                    
**Suggestions:**
- Try different keywords
- Upload more documents first
- Use broader search terms
- Check spelling

**Total documents available:** {total_docs}""", "info")
            
            return create_search_results(query, results, total_docs)
        else:
            return create_search_status(f"❌ Search failed: {response.text}", "error")
    
    except Exception as e:
        return create_search_status(f"❌ Search error: {str(e)}", "error")

def create_search_results(query: str, results: List[Dict], total_docs: int) -> str:
    """Create beautiful animated search results"""
    results_html = ""
    for i, result in enumerate(results):
        relevance = result.get('relevance_score', 0)
        relevance_color = "#4CAF50" if relevance > 80 else "#ff9800" if relevance > 60 else "#f44336"
        
        results_html += f"""
        <div class="search-result animate-slide-up" style="animation-delay: {i * 0.1}s;">
            <div class="result-header">
                <div class="result-title">📄 {result.get('filename', 'Unknown File')}</div>
                <div class="result-relevance" style="background-color: {relevance_color};">
                    {relevance}% match
                </div>
            </div>
            <div class="result-content">
                <div class="result-preview">
                    {result.get('content_preview', 'No preview available')[:300]}{'...' if len(result.get('content_preview', '')) > 300 else ''}
                </div>
                <div class="result-matches">
                    📍 {result.get('matches', 1)} match{'es' if result.get('matches', 1) != 1 else ''} found
                </div>
            </div>
        </div>
        """
    
    return f"""
<div class="search-results animate-bounce-in">
    <div class="search-header">
        <div class="search-icon animate-pulse">🔍</div>
        <div class="search-title">Found {len(results)} results for "{query}"</div>
        <div class="search-subtitle">Searched across {total_docs} documents</div>
    </div>
    
    <div class="results-container">
        {results_html}
    </div>
    
    <div class="search-tips animate-fade-in" style="animation-delay: 0.8s;">
        <div class="tip-header">💡 <strong>Search Tips:</strong></div>
        <div class="tips-list">
            • Use specific keywords from your documents<br>
            • Try searching for concepts, formulas, or definitions<br>
            • Combine multiple keywords for better results<br>
            • Ask the AI questions about these search results!
        </div>
    </div>
</div>
    """

def create_search_status(message: str, status_type: str) -> str:
    """Create search status message"""
    return create_status_card(message, status_type)

def clean_for_tts(text: str) -> str:
    """Clean text for text-to-speech"""
    import re
    
    # Remove emojis and special characters
    text = re.sub(r'[🤖🎓🚀📊🧠❌🚫⚡🔥💡🎤🔊📚🌍📄🔍🎯💪✨🌟💫🏆]', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\n+', '. ', text)
    
    # Make abbreviations speech-friendly
    text = text.replace('AI', 'A I')
    text = text.replace('LLM', 'Language Model')
    text = text.replace('RAG', 'R A G')
    text = text.replace('API', 'A P I')
    
    # Limit length for TTS
    sentences = text.split('.')
    if len(sentences) > 3:
        text = '. '.join(sentences[:3]) + '.'
    
    return text.strip()

def clear_chat():
    """Clear chat history"""
    return [], ""

def create_ultimate_interface():
    """Create the ultimate interface with all features"""
    
    # Ultimate CSS with all animations
    ultimate_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --shadow-light: 0 8px 32px rgba(0, 0, 0, 0.1);
        --shadow-heavy: 0 20px 60px rgba(0, 0, 0, 0.2);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    .gradio-container {
        background: var(--primary-gradient) !important;
        color: white !important;
        min-height: 100vh !important;
    }
    
    /* Animation keyframes */
    @keyframes bounce-in {
        0% { transform: scale(0) rotate(-180deg); opacity: 0; }
        50% { transform: scale(1.2) rotate(-10deg); opacity: 0.8; }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    
    @keyframes slide-up {
        0% { transform: translateY(50px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fade-in {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(79, 172, 254, 0.3); }
        50% { box-shadow: 0 0 40px rgba(79, 172, 254, 0.7); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes typing {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Apply animations */
    .animate-bounce-in { animation: bounce-in 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .animate-slide-up { animation: slide-up 0.6s ease-out; }
    .animate-fade-in { animation: fade-in 0.5s ease-out; }
    .animate-pulse { animation: pulse 2s infinite; }
    .animate-glow { animation: glow 2s ease-in-out infinite; }
    .animate-float { animation: float 3s ease-in-out infinite; }
    .animate-shake { animation: shake 0.5s ease-out; }
    .animate-typing { animation: typing 1.5s ease-in-out infinite; }
    
    /* Ultimate cards */
    .ultimate-card {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        padding: 32px !important;
        margin: 20px 0 !important;
        border: 2px solid var(--glass-border) !important;
        box-shadow: var(--shadow-light) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .ultimate-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent) !important;
    }
    
    .ultimate-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: var(--shadow-heavy) !important;
        border-color: rgba(79, 172, 254, 0.5) !important;
    }
    
    /* Voice button - ultimate version */
    .ultimate-voice-btn {
        background: var(--accent-gradient) !important;
        border: 4px solid white !important;
        border-radius: 50% !important;
        width: 160px !important;
        height: 160px !important;
        font-size: 4rem !important;
        color: white !important;
        cursor: pointer !important;
        margin: 30px auto !important;
        display: block !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 20px 60px rgba(79, 172, 254, 0.4) !important;
    }
    
    .ultimate-voice-btn::before {
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        left: -50% !important;
        width: 200% !important;
        height: 200% !important;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent) !important;
        transform: rotate(45deg) !important;
        transition: all 0.6s ease !important;
    }
    
    .ultimate-voice-btn:hover {
        transform: scale(1.1) rotateZ(5deg) !important;
        box-shadow: 0 30px 80px rgba(79, 172, 254, 0.6) !important;
    }
    
    .ultimate-voice-btn:hover::before {
        animation: shine 0.8s ease-in-out !important;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .ultimate-voice-btn.listening {
        background: var(--success-gradient) !important;
        animation: glow 1s infinite, pulse 2s infinite !important;
    }
    
    .ultimate-voice-btn.processing {
        background: linear-gradient(135deg, #ff9800, #f57c00) !important;
        animation: typing 1.5s infinite !important;
    }
    
    /* Status cards */
    .status-card {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin: 16px 0 !important;
        border: 2px solid var(--glass-border) !important;
        text-align: center !important;
    }
    
    .status-card.success { border-color: rgba(76, 175, 80, 0.6) !important; }
    .status-card.error { border-color: rgba(244, 67, 54, 0.6) !important; }
    .status-card.warning { border-color: rgba(255, 152, 0, 0.6) !important; }
    .status-card.info { border-color: rgba(33, 150, 243, 0.6) !important; }
    
    .status-content {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 16px !important;
    }
    
    .status-icon {
        font-size: 2rem !important;
    }
    
    .status-message {
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
    }
    
    /* Login success */
    .login-success {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        padding: 32px !important;
        text-align: center !important;
        border: 2px solid rgba(76, 175, 80, 0.4) !important;
    }
    
    .success-header {
        margin-bottom: 24px !important;
    }
    
    .success-icon {
        font-size: 4rem !important;
        margin-bottom: 16px !important;
    }
    
    .success-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #4CAF50 !important;
        margin-bottom: 8px !important;
    }
    
    .success-subtitle {
        font-size: 1.2rem !important;
        opacity: 0.9 !important;
    }
    
    .model-status {
        margin: 24px 0 !important;
    }
    
    .status-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)) !important;
        gap: 16px !important;
        margin: 20px 0 !important;
    }
    
    .status-item {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .status-item:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    .status-icon {
        font-size: 1.5rem !important;
    }
    
    .status-label {
        font-size: 0.9rem !important;
        opacity: 0.8 !important;
    }
    
    .status-value {
        font-weight: 600 !important;
        color: #4CAF50 !important;
    }
    
    .welcome-features {
        margin: 24px 0 !important;
    }
    
    .feature-item {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
    }
    
    .feature-icon {
        font-size: 1.3rem !important;
    }
    
    .ready-message {
        background: var(--accent-gradient) !important;
        padding: 16px 24px !important;
        border-radius: 16px !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 24px !important;
    }
    
    /* Upload success */
    .upload-success {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        padding: 32px !important;
        border: 2px solid rgba(76, 175, 80, 0.4) !important;
    }
    
    .upload-stats {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 20px !important;
        margin: 24px 0 !important;
    }
    
    .stat-item {
        text-align: center !important;
        padding: 20px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stat-number {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #4CAF50 !important;
        line-height: 1 !important;
    }
    
    .stat-label {
        font-size: 1rem !important;
        opacity: 0.8 !important;
        margin-top: 8px !important;
    }
    
    .uploaded-files {
        margin: 24px 0 !important;
    }
    
    .uploaded-file {
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        padding: 16px !important;
        margin: 12px 0 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(5px) !important;
        transition: all 0.3s ease !important;
    }
    
    .uploaded-file:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(4px) !important;
    }
    
    .file-icon {
        font-size: 2rem !important;
        color: #4CAF50 !important;
    }
    
    .file-info {
        flex: 1 !important;
    }
    
    .file-name {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 4px !important;
    }
    
    .file-details {
        font-size: 0.9rem !important;
        opacity: 0.8 !important;
    }
    
    .file-status {
        font-size: 1.5rem !important;
        color: #4CAF50 !important;
    }
    
    .upload-tip {
        background: var(--accent-gradient) !important;
        padding: 16px 24px !important;
        border-radius: 16px !important;
        text-align: center !important;
        margin-top: 24px !important;
    }
    
    /* Search results */
    .search-results {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        padding: 32px !important;
        border: 2px solid var(--glass-border) !important;
    }
    
    .search-header {
        text-align: center !important;
        margin-bottom: 24px !important;
    }
    
    .search-icon {
        font-size: 3rem !important;
        margin-bottom: 12px !important;
    }
    
    .search-title {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
    }
    
    .search-subtitle {
        opacity: 0.8 !important;
    }
    
    .results-container {
        margin: 24px 0 !important;
    }
    
    .search-result {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin: 16px 0 !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .search-result:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
    }
    
    .result-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 12px !important;
    }
    
    .result-title {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    .result-relevance {
        color: white !important;
        padding: 6px 12px !important;
        border-radius: 20px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    
    .result-content {
        margin-top: 12px !important;
    }
    
    .result-preview {
        background: rgba(255, 255, 255, 0.1) !important;
        padding: 12px !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        margin-bottom: 8px !important;
    }
    
    .result-matches {
        font-size: 0.85rem !important;
        opacity: 0.7 !important;
    }
    
    .search-tips {
        background: var(--accent-gradient) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-top: 24px !important;
    }
    
    .tip-header {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 12px !important;
    }
    
    .tips-list {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        opacity: 0.9 !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .ultimate-card {
            margin: 12px 5px !important;
            padding: 20px !important;
        }
        
        .ultimate-voice-btn {
            width: 120px !important;
            height: 120px !important;
            font-size: 3rem !important;
        }
        
        .upload-stats, .status-grid {
            grid-template-columns: 1fr !important;
        }
        
        .success-title {
            font-size: 1.5rem !important;
        }
        
        .stat-number {
            font-size: 2rem !important;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3) !important;
        border-radius: 4px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5) !important;
    }
    """
    
    # Ultimate JavaScript with all voice features
    ultimate_js = """
    <script>
    console.log('🚀 Initializing Ultimate Quantized LLM Voice System...');
    
    // Ultimate voice system
    let recognition = null;
    let synthesis = window.speechSynthesis;
    let isListening = false;
    let isProcessing = false;
    let voices = [];
    let lastTTSText = '';
    let confidence = 0;
    
    // Language configuration
    const languages = {
        'en': { code: 'en-US', name: 'English', flag: '🇺🇸' },
        'ta': { code: 'ta-IN', name: 'Tamil', flag: '🇮🇳' },
        'hi': { code: 'hi-IN', name: 'Hindi', flag: '🇮🇳' },
        'es': { code: 'es-ES', name: 'Spanish', flag: '🇪🇸' },
        'fr': { code: 'fr-FR', name: 'French', flag: '🇫🇷' },
        'de': { code: 'de-DE', name: 'German', flag: '🇩🇪' }
    };
    
    function initUltimateVoice() {
        console.log('🎤 Setting up ultimate voice recognition...');
        
        // Load voices
        synthesis.addEventListener('voiceschanged', loadVoices);
        loadVoices();
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            recognition = new SpeechRecognition();
            setupUltimateRecognition();
        } else {
            console.warn('⚠️ Speech recognition not supported');
            updateVoiceStatus('❌ Voice not supported - Please use Chrome or Edge', 'error');
            return false;
        }
        
        console.log('✅ Ultimate voice system ready!');
        updateVoiceStatus('🎤 Ultimate voice ready - Click the big button to start!', 'ready');
        return true;
    }
    
    function loadVoices() {
        voices = synthesis.getVoices();
        console.log(`🎙️ Loaded ${voices.length} voices for TTS`);
    }
    
    function setupUltimateRecognition() {
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 5;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            console.log('🎤 Ultimate voice recognition started');
            isListening = true;
            updateVoiceButton('listening');
            updateVoiceStatus('🎤 Listening... Speak clearly!', 'listening');
            playStartSound();
        };
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            let confidence = 0;
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                const transcript = result[0].transcript;
                confidence = Math.max(confidence, result[0].confidence || 0.8);
                
                if (result.isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Show interim results with typing animation
            if (interimTranscript) {
                updateVoiceStatus(`🎤 Hearing: "${interimTranscript}..." 🎯 ${Math.round(confidence * 100)}%`, 'processing');
            }
            
            if (finalTranscript) {
                console.log(`✅ Final transcript: "${finalTranscript}" (${Math.round(confidence * 100)}% confidence)`);
                fillMessageInput(finalTranscript);
                
                const confidenceLevel = confidence > 0.8 ? 'High' : confidence > 0.6 ? 'Medium' : 'Low';
                updateVoiceStatus(`✅ Captured: "${finalTranscript}" | Confidence: ${confidenceLevel} (${Math.round(confidence * 100)}%)`, 'success');
                
                if (confidence > 0.7) {
                    playSuccessSound();
                } else {
                    playWarningSound();
                }
            }
        };
        
        recognition.onerror = function(event) {
            console.error('❌ Voice recognition error:', event.error);
            isListening = false;
            updateVoiceButton('error');
            
            let errorMessage = '';
            let suggestions = '';
            
            switch(event.error) {
                case 'network':
                    errorMessage = '📶 Network issue detected';
                    suggestions = 'Check your internet connection and try again';
                    break;
                case 'not-allowed':
                    errorMessage = '🎤 Microphone access denied';
                    suggestions = 'Please allow microphone access in browser settings';
                    break;
                case 'no-speech':
                    errorMessage = '🤫 No speech detected';
                    suggestions = 'Speak closer to microphone or increase volume';
                    break;
                case 'audio-capture':
                    errorMessage = '🎤 Microphone not found';
                    suggestions = 'Check if microphone is connected and working';
                    break;
                case 'language-not-supported':
                    errorMessage = '🌍 Language not supported';
                    suggestions = 'Try switching to English or another supported language';
                    break;
                default:
                    errorMessage = `❌ Voice error: ${event.error}`;
                    suggestions = 'Try refreshing the page or using a different browser';
            }
            
            updateVoiceStatus(`${errorMessage} | 💡 ${suggestions}`, 'error');
            playErrorSound();
        };
        
        recognition.onend = function() {
            console.log('🏁 Voice recognition ended');
            isListening = false;
            if (!isProcessing) {
                updateVoiceButton('ready');
                updateVoiceStatus('🎤 Click the microphone to speak again', 'ready');
            }
        };
    }
    
    function startUltimateVoice() {
        if (!recognition) {
            initUltimateVoice();
            return;
        }
        
        if (isListening) {
            stopVoiceInput();
            return;
        }
        
        try {
            // Get current language from dropdown if available
            const langSelect = document.querySelector('select');
            if (langSelect && languages[langSelect.value]) {
                recognition.lang = languages[langSelect.value].code;
                console.log(`🌍 Using language: ${languages[langSelect.value].name} (${languages[langSelect.value].code})`);
            }
            
            recognition.start();
            updateVoiceStatus('🎤 Starting ultimate voice recognition...', 'starting');
        } catch (error) {
            console.error('❌ Failed to start voice recognition:', error);
            updateVoiceStatus('❌ Could not start voice input - Try again', 'error');
            playErrorSound();
        }
    }
    
    function stopVoiceInput() {
        if (recognition && isListening) {
            recognition.stop();
            updateVoiceStatus('🛑 Stopping voice input...', 'stopping');
        }
    }
    
    function speakUltimateText(text) {
        if (!text || !text.trim()) return;
        
        console.log('🔊 Ultimate TTS speaking:', text.substring(0, 100) + '...');
        
        synthesis.cancel();
        
        const cleanText = cleanUltimateText(text);
        
        if (cleanText.length > 800) {
            // Split into sentences for long text
            const sentences = cleanText.split(/[.!?]+/).filter(s => s.trim().length > 0);
            speakSentences(sentences.slice(0, 5), 0); // Limit to 5 sentences
        } else {
            speakSingleText(cleanText);
        }
    }
    
    function cleanUltimateText(text) {
        // Ultimate text cleaning for TTS
        let clean = text
            .replace(/[🤖🎓🚀📊🧠❌🚫⚡🔥💡🎤🔊📚🌍📄🔍🎯💪✨🌟💫🏆]/g, '')
            .replace(/\\*\\*(.*?)\\*\\*/g, '$1')
            .replace(/\\*(.*?)\\*/g, '$1')
            .replace(/#{1,6}\\s/g, '')
            .replace(/```[\\s\\S]*?```/g, '')
            .replace(/\\n+/g, '. ')
            .replace(/\\s+/g, ' ')
            .trim();
        
        // Make technical terms more speech-friendly
        const replacements = {
            'AI': 'A I',
            'LLM': 'Large Language Model',
            'RAG': 'R A G',
            'API': 'A P I',
            'TTS': 'text to speech',
            'STT': 'speech to text',
            'GPU': 'G P U',
            'CPU': 'C P U',
            'UI': 'user interface',
            'URL': 'U R L',
            'PDF': 'P D F'
        };
        
        for (const [abbrev, expansion] of Object.entries(replacements)) {
            clean = clean.replace(new RegExp('\\\\b' + abbrev + '\\\\b', 'g'), expansion);
        }
        
        return clean;
    }
    
    function speakSingleText(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Ultimate TTS settings
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Select best voice
        const voice = selectBestVoice();
        if (voice) {
            utterance.voice = voice;
        }
        
        utterance.onstart = function() {
            updateVoiceStatus('🔊 AI is speaking... (Click to interrupt)', 'speaking');
            updateVoiceButton('speaking');
        };
        
        utterance.onend = function() {
            updateVoiceStatus('🎤 Click microphone to continue conversation', 'ready');
            updateVoiceButton('ready');
        };
        
        utterance.onerror = function(event) {
            console.error('❌ TTS error:', event.error);
            updateVoiceStatus('❌ Could not speak response', 'error');
            updateVoiceButton('ready');
        };
        
        synthesis.speak(utterance);
    }
    
    function speakSentences(sentences, index) {
        if (index >= sentences.length) {
            updateVoiceStatus('🎤 Click microphone for more questions', 'ready');
            updateVoiceButton('ready');
            return;
        }
        
        const sentence = sentences[index].trim();
        if (sentence.length < 5) {
            speakSentences(sentences, index + 1);
            return;
        }
        
        const utterance = new SpeechSynthesisUtterance(sentence);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        const voice = selectBestVoice();
        if (voice) utterance.voice = voice;
        
        utterance.onend = function() {
            setTimeout(() => speakSentences(sentences, index + 1), 800);
        };
        
        utterance.onerror = function() {
            speakSentences(sentences, index + 1);
        };
        
        synthesis.speak(utterance);
    }
    
    function selectBestVoice() {
        if (!voices.length) return null;
        
        // Prefer Google or Microsoft voices for better quality
        const preferred = voices.find(voice => 
            voice.name.includes('Google') || 
            voice.name.includes('Microsoft') ||
            voice.name.includes('Natural')
        );
        
        return preferred || voices.find(voice => voice.lang.startsWith('en')) || voices[0];
    }
    
    function updateVoiceButton(state) {
        const btn = document.getElementById('ultimate-voice-btn');
        if (!btn) return;
        
        btn.className = 'ultimate-voice-btn';
        
        switch(state) {
            case 'listening':
                btn.className += ' listening';
                btn.innerHTML = '🔴';
                btn.title = 'Listening... Click to stop';
                break;
            case 'speaking':
                btn.className += ' animate-glow';
                btn.innerHTML = '🔊';
                btn.title = 'AI is speaking... Click to interrupt';
                break;
            case 'processing':
                btn.className += ' processing';
                btn.innerHTML = '⏳';
                btn.title = 'Processing your speech...';
                break;
            case 'error':
                btn.className += ' animate-shake';
                btn.innerHTML = '❌';
                btn.title = 'Voice error - Click to retry';
                break;
            case 'ready':
            default:
                btn.className += ' animate-float';
                btn.innerHTML = '🎤';
                btn.title = 'Click to start ultimate voice input';
                break;
        }
    }
    
    function updateVoiceStatus(message, type = 'info') {
        const statusElements = document.querySelectorAll('.voice-status');
        statusElements.forEach(element => {
            element.textContent = message;
            element.className = `voice-status ${type} animate-typing`;
        });
        console.log(`Voice Status (${type}):`, message);
    }
    
    function fillMessageInput(text) {
        const textareas = document.querySelectorAll('textarea');
        
        for (let textarea of textareas) {
            const label = textarea.parentElement?.querySelector('label')?.textContent || '';
            const placeholder = textarea.placeholder || '';
            
            if (label.toLowerCase().includes('chat') || 
                label.toLowerCase().includes('message') ||
                placeholder.toLowerCase().includes('ask') ||
                placeholder.toLowerCase().includes('chat')) {
                
                textarea.value = text;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.focus();
                
                // Visual feedback
                textarea.style.background = 'rgba(79, 172, 254, 0.2)';
                textarea.style.transition = 'all 0.3s ease';
                setTimeout(() => {
                    textarea.style.background = '';
                }, 2000);
                
                break;
            }
        }
    }
    
    // Audio feedback functions
    function playStartSound() {
        playTone([800, 1000], [0.1, 0.1]);
    }
    
    function playSuccessSound() {
        playTone([523.25, 659.25, 783.99], [0.15, 0.15, 0.15]);
    }
    
    function playWarningSound() {
        playTone([400, 600], [0.1, 0.1]);
    }
    
    function playErrorSound() {
        playTone([300, 200], [0.15, 0.15]);
    }
    
    function playTone(frequencies, durations) {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            let startTime = audioContext.currentTime;
            
            frequencies.forEach((freq, index) => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(freq, startTime);
                gainNode.gain.setValueAtTime(0.1, startTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + durations[index]);
                
                oscillator.start(startTime);
                oscillator.stop(startTime + durations[index]);
                
                startTime += durations[index] + 0.05;
            });
        } catch (e) {
            // Silently fail if audio context not available
        }
    }
    
    // Auto-speak TTS responses
    setInterval(function() {
        const ttsElements = document.querySelectorAll('textarea[style*="display: none"], textarea[data-tts="true"]');
        
        for (let element of ttsElements) {
            if (element.value && element.value !== lastTTSText && element.value.length > 20) {
                lastTTSText = element.value;
                
                let textToSpeak = element.value;
                if (textToSpeak.startsWith('TTS:')) {
                    textToSpeak = textToSpeak.replace('TTS:', '').trim();
                }
                
                speakUltimateText(textToSpeak);
                break;
            }
        }
    }, 2000);
    
    // Initialize when page loads
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎓 Ultimate interface loaded');
        setTimeout(() => {
            if (initUltimateVoice()) {
                updateVoiceStatus('🚀 Ultimate voice system ready! Click the big microphone to start.', 'ready');
            }
        }, 1500);
    });
    
    // Make functions globally available
    window.startUltimateVoice = startUltimateVoice;
    window.speakUltimateText = speakUltimateText;
    window.stopVoiceInput = stopVoiceInput;
    
    console.log('🎉 Ultimate Quantized LLM Voice System loaded!');
    </script>
    """
    
    with gr.Blocks(css=ultimate_css, title="🤖 Ultimate Quantized LLM Chatbot") as app:
        
        # Ultimate Header
        gr.HTML("""
        <div class="ultimate-card animate-bounce-in">
            <div style="text-align: center;">
                <h1 style="font-size: 4rem; margin-bottom: 20px; background: linear-gradient(45deg, #4facfe, #00f2fe, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; text-shadow: 0 0 30px rgba(79, 172, 254, 0.3);">
                    🤖 Ultimate Quantized LLM
                </h1>
                <h2 style="font-size: 2.5rem; margin-bottom: 24px; opacity: 0.95; font-weight: 700; background: linear-gradient(45deg, #f093fb, #f5576c); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    AI Chatbot Experience
                </h2>
                <p style="font-size: 1.4rem; opacity: 0.85; line-height: 1.6; max-width: 800px; margin: 0 auto;">
                    🧠 <strong>Real AI Responses</strong> • 🎤 <strong>Ultimate Voice</strong> • 📚 <strong>Smart Documents</strong> • 🌍 <strong>6 Languages</strong>
                </p>
                <div style="margin-top: 24px; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 16px; backdrop-filter: blur(10px);">
                    <span style="font-size: 1.1rem; font-weight: 600;">✨ The most advanced voice-enabled AI chatbot with real quantized models ✨</span>
                </div>
            </div>
        </div>
        """)
        
        # Ultimate Voice Section
        gr.HTML(f"""
        <div class="ultimate-card animate-slide-up">
            <div style="text-align: center;">
                <h3 style="font-size: 2.2rem; margin-top: 0; margin-bottom: 20px; background: linear-gradient(45deg, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">
                    🎤 Ultimate Voice Interface
                </h3>
                
                <button id="ultimate-voice-btn" class="ultimate-voice-btn animate-float" onclick="startUltimateVoice()" title="Click to start ultimate voice input">
                    🎤
                </button>
                
                <div class="voice-status animate-typing" style="color: white; font-size: 1.4rem; font-weight: 600; text-align: center; margin: 24px; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 20px; backdrop-filter: blur(10px); border: 2px solid rgba(255,255,255,0.2);">
                    🚀 Ultimate voice system loading... Please wait
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 32px;">
                    <div class="status-item animate-fade-in" style="animation-delay: 0.2s;">
                        <div class="status-icon">🇺🇸</div>
                        <div class="status-info">
                            <div class="status-value">English</div>
                        </div>
                    </div>
                    <div class="status-item animate-fade-in" style="animation-delay: 0.3s;">
                        <div class="status-icon">🇮🇳</div>
                        <div class="status-info">
                            <div class="status-value">Tamil</div>
                        </div>
                    </div>
                    <div class="status-item animate-fade-in" style="animation-delay: 0.4s;">
                        <div class="status-icon">🇮🇳</div>
                        <div class="status-info">
                            <div class="status-value">Hindi</div>
                        </div>
                    </div>
                    <div class="status-item animate-fade-in" style="animation-delay: 0.5s;">
                        <div class="status-icon">🇪🇸</div>
                        <div class="status-info">
                            <div class="status-value">Spanish</div>
                        </div>
                    </div>
                    <div class="status-item animate-fade-in" style="animation-delay: 0.6s;">
                        <div class="status-icon">🇫🇷</div>
                        <div class="status-info">
                            <div class="status-value">French</div>
                        </div>
                    </div>
                    <div class="status-item animate-fade-in" style="animation-delay: 0.7s;">
                        <div class="status-icon">🇩🇪</div>
                        <div class="status-info">
                            <div class="status-value">German</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Login Section
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML('<div class="ultimate-card"><h3 style="margin-top: 0; font-size: 1.8rem;">🔐 Connect to Quantized AI Backend</h3></div>')
                
                with gr.Row():
                    username_input = gr.Textbox(
                        label="👤 Username", 
                        placeholder="Enter any username for demo",
                        elem_classes=["ultimate-input"]
                    )
                    password_input = gr.Textbox(
                        label="🔑 Password", 
                        type="password", 
                        placeholder="Enter any password for demo",
                        elem_classes=["ultimate-input"]
                    )
                    login_btn = gr.Button("🚀 Connect to AI", variant="primary", elem_classes=["ultimate-button"])
                
                login_status = gr.HTML(create_status_card(
                    """🤖 **Ready to Connect to Your Quantized AI**
                    
Enter any username and password to access your real AI backend with:
• Actual quantized model responses
• Working document upload & RAG
• Enhanced voice in 6 languages
• Smart search across documents

Make sure your backend is running first! 🚀""", "info"))
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="ultimate-card animate-slide-up">
                    <h4 style="color: #4facfe; margin-top: 0; font-size: 1.6rem;">🚀 Ultimate Features</h4>
                    <div style="color: rgba(255,255,255,0.9); line-height: 1.8;">
                        <div class="feature-item" style="margin: 16px 0; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 12px;">
                            <span class="feature-icon">🧠</span>
                            <div>
                                <div style="font-weight: 700; font-size: 1.1rem;">Real Quantized AI</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Actual model responses, not demos</div>
                            </div>
                        </div>
                        
                        <div class="feature-item" style="margin: 16px 0; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 12px;">
                            <span class="feature-icon">🎤</span>
                            <div>
                                <div style="font-weight: 700; font-size: 1.1rem;">Ultimate Voice</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">6 languages, real-time transcription</div>
                            </div>
                        </div>
                        
                        <div class="feature-item" style="margin: 16px 0; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 12px;">
                            <span class="feature-icon">📚</span>
                            <div>
                                <div style="font-weight: 700; font-size: 1.1rem;">Smart Documents</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Upload, analyze, Q&A with RAG</div>
                            </div>
                        </div>
                        
                        <div class="feature-item" style="margin: 16px 0; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 12px;">
                            <span class="feature-icon">⚡</span>
                            <div>
                                <div style="font-weight: 700; font-size: 1.1rem;">Lightning Fast</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Quantized models for speed</div>
                            </div>
                        </div>
                    </div>
                </div>
                """)
        
        # Main Chat Interface
        with gr.Row():
            with gr.Column(scale=3):
                # Chat Interface
                chatbot = gr.Chatbot(
                    height=600,
                    show_label=False,
                    elem_classes=["ultimate-chatbot"]
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        label="💬 Chat with Ultimate Quantized AI", 
                        placeholder="Ask me anything... math, science, coding, or use the ultimate voice button above! 🎤",
                        lines=3,
                        scale=4,
                        elem_classes=["ultimate-input"]
                    )
                    language_select = gr.Dropdown(
                        choices=["en", "ta", "hi", "es", "fr", "de"],
                        value="en",
                        label="🌍 Language",
                        scale=1,
                        elem_classes=["ultimate-select"]
                    )
                
                with gr.Row():
                    send_btn = gr.Button("🚀 Send to AI", variant="primary", scale=2, elem_classes=["ultimate-button"])
                    voice_chat_btn = gr.Button("🎤 Voice Chat", variant="secondary", scale=1, elem_classes=["ultimate-button"])
                    clear_btn = gr.Button("🧹 Clear Chat", variant="secondary", scale=1, elem_classes=["ultimate-button"])
                
                # Hidden TTS output
                tts_output = gr.Textbox(
                    visible=False,
                    interactive=False,
                    elem_id="ultimate-tts-output"
                )
            
            with gr.Column(scale=1):
                # Ultimate Document Upload
                gr.HTML('<div class="ultimate-card"><h3 style="margin-top: 0; font-size: 1.6rem;">📚 Ultimate Document Processing</h3></div>')
                
                file_upload = gr.File(
                    label="📎 Drop Your Files Here",
                    file_types=[".txt", ".md", ".pdf", ".docx", ".py", ".json", ".csv"],
                    file_count="multiple",
                    elem_classes=["ultimate-upload"]
                )
                
                upload_btn = gr.Button(
                    "📤 Process with Quantized AI", 
                    variant="primary",
                    elem_classes=["ultimate-button"]
                )
                
                upload_result = gr.HTML(create_status_card(
                    """📚 **Ultimate Document Processing Ready**
                    
Upload any documents and your quantized AI will:
• Analyze content with real embeddings
• Create searchable chunks for RAG
• Extract topics and key information  
• Enable intelligent Q&A

**Supported:** PDF, DOCX, TXT, MD, JSON, CSV, PY files

Drag and drop multiple files at once! ✨""", "info"))
                
                # Ultimate Search
                gr.HTML('<div class="ultimate-card" style="margin-top: 20px;"><h3 style="margin-top: 0; font-size: 1.6rem;">🔍 Ultimate AI Search</h3></div>')
                
                search_input = gr.Textbox(
                    label="Search Your Documents",
                    placeholder="Search for concepts, code, formulas, definitions...",
                    elem_classes=["ultimate-input"]
                )
                
                search_btn = gr.Button(
                    "🔍 Search with AI", 
                    variant="primary",
                    elem_classes=["ultimate-button"]
                )
                
                search_results = gr.HTML(create_status_card(
                    """🔍 **Ultimate AI Search Ready**
                    
Once you upload documents, use this powerful search to:
• Find information across all your files
• Get relevance scores with AI ranking
• See context snippets with highlights
• Ask follow-up questions about results

The search uses real embeddings and vector similarity! 🚀""", "info"))
        
        # Ultimate Footer
        gr.HTML(f"""
        <div class="ultimate-card animate-slide-up" style="margin-top: 40px;">
            <div style="text-align: center;">
                <h3 style="color: #4facfe; margin-bottom: 20px; font-size: 2rem; font-weight: 700;">
                    🌟 Ultimate Quantized LLM Experience 🌟
                </h3>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 32px 0;">
                    
                    <div class="feature-item animate-fade-in" style="animation-delay: 0.2s; padding: 24px; background: rgba(255,255,255,0.1); border-radius: 16px;">
                        <div style="font-size: 2.5rem; margin-bottom: 12px;">🧠</div>
                        <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 8px;">Real AI Power</div>
                        <div style="font-size: 1rem; opacity: 0.85; line-height: 1.4;">Genuine quantized language models with actual inference, not simulated responses</div>
                    </div>
                    
                    <div class="feature-item animate-fade-in" style="animation-delay: 0.4s; padding: 24px; background: rgba(255,255,255,0.1); border-radius: 16px;">
                        <div style="font-size: 2.5rem; margin-bottom: 12px;">🎤</div>
                        <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 8px;">Voice Excellence</div>
                        <div style="font-size: 1rem; opacity: 0.85; line-height: 1.4;">Ultimate speech recognition with confidence scoring and natural TTS</div>
                    </div>
                    
                    <div class="feature-item animate-fade-in" style="animation-delay: 0.6s; padding: 24px; background: rgba(255,255,255,0.1); border-radius: 16px;">
                        <div style="font-size: 2.5rem; margin-bottom: 12px;">📚</div>
                        <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 8px;">Smart Documents</div>
                        <div style="font-size: 1rem; opacity: 0.85; line-height: 1.4;">Working RAG system with real embeddings and vector search</div>
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 20px; padding: 24px; margin: 32px 0; box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);">
                    <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 12px;">
                        🚀 Ready for the Ultimate AI Experience? 🚀
                    </div>
                    <div style="font-size: 1.1rem; opacity: 0.95; line-height: 1.5;">
                        Connect to your quantized backend, upload documents, and experience the future of AI interaction with voice, vision, and intelligence combined!
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Add Ultimate JavaScript
        gr.HTML(ultimate_js)
        
        # Ultimate Event Handlers
        login_btn.click(
            fn=login_user, 
            inputs=[username_input, password_input], 
            outputs=[login_status]
        )
        
        send_btn.click(
            fn=ultimate_chat_with_ai,
            inputs=[message_input, chatbot], 
            outputs=[chatbot, message_input, tts_output]
        )
        
        voice_chat_btn.click(
            fn=lambda msg, hist: ultimate_chat_with_ai(msg, hist),
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, tts_output]
        )
        
        message_input.submit(
            fn=ultimate_chat_with_ai,
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, tts_output]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, message_input]
        )
        
        upload_btn.click(
            fn=ultimate_upload_documents,
            inputs=[file_upload],
            outputs=[upload_result]
        )
        
        search_btn.click(
            fn=ultimate_search_documents,
            inputs=[search_input],
            outputs=[search_results]
        )
        
        # Language change handler
        language_select.change(
            fn=lambda lang: print(f"Language changed to: {lang}"),
            inputs=[language_select]
        )
    
    return app

if __name__ == "__main__":
    logger.info("🚀 Starting Ultimate Quantized LLM Chatbot...")
    
    print("🤖 ULTIMATE QUANTIZED LLM CHATBOT")
    print("=" * 40)
    print("✅ Real AI responses with quantized models")
    print("✅ Working document upload with RAG")
    print("✅ Ultimate voice system (6 languages)")
    print("✅ Beautiful animated interface")
    print("✅ Production-ready features")
    print("✅ Compatible with your Phase 5 setup")
    print("")
    print("🔧 Make sure your backend is running:")
    print("   python enhanced_backend.py")
    print("")
    print("🌐 Then access at: http://localhost:7860")
    print("=" * 40)
    
    app = create_ultimate_interface()
    
    try:
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            show_api=False
        )
    except Exception as e:
        logger.error(f"Failed to launch: {e}")
        print(f"❌ Launch error: {e}")
        print("💡 Make sure port 7860 is free and try again")
