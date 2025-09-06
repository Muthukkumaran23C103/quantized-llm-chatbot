#!/usr/bin/env python3
"""
Enhanced Frontend for Quantized LLM Chatbot - Phase 5 Extension
Builds on existing gradio_ui.py with working AI interaction and document upload
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - connecting to your existing backend
API_BASE = "http://localhost:8000"
UPLOAD_DIR = Path("./data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Global state
class ChatbotState:
    def __init__(self):
        self.auth_token = None
        self.username = None
        self.conversation_history = []
        self.current_language = "en"
        self.voice_enabled = True
        self.backend_connected = False

state = ChatbotState()

def check_backend_connection() -> bool:
    """Check if your Phase 5 backend is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            state.backend_connected = True
            return True
    except:
        state.backend_connected = False
    return False

def login_user(username: str, password: str) -> str:
    """Login with your existing backend"""
    if not username or not password:
        return "❌ Please enter both username and password"
    
    try:
        if not check_backend_connection():
            return """🚫 **Backend Not Connected**
            
Please start your Phase 5 backend first:
```bash
cd /home/zen/quantized-llm-chatbot
python enhanced_backend.py
```
Then refresh and try logging in again."""
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            state.auth_token = data.get("access_token")
            state.username = username
            
            # Get model status
            try:
                model_response = requests.get(f"{API_BASE}/models/status", timeout=5)
                if model_response.status_code == 200:
                    model_info = model_response.json()
                    return f"""✅ **Welcome {username}! Phase 5 Backend Connected**

🤖 **Quantized LLM Status:**
- Model Loaded: {'✅' if model_info.get('loaded') else '⚠️ Loading...'}  
- Model: {model_info.get('model_name', 'Unknown')}
- Device: {model_info.get('device', 'CPU')}
- Documents: {model_info.get('documents_count', 0)} uploaded

🚀 **Ready for AI interaction!**"""
                
            except:
                pass
            
            return f"""✅ **Welcome {username}!**
            
🤖 **Quantized LLM Chatbot Ready**
🎤 Voice features enabled  
📚 Document processing active
🧠 AI backend connected

**Start chatting with your AI!** 🚀"""
        else:
            return "❌ **Login Failed** - Check credentials"
            
    except Exception as e:
        return f"🚫 **Connection Error** - {str(e)}"

def chat_with_ai(message: str, history: List) -> Tuple[List, str, str]:
    """Enhanced chat that actually connects to your AI backend"""
    if not state.auth_token:
        if history is None:
            history = []
        history.append([message, "🔐 **Please log in first to access the AI!**"])
        return history, "", ""
    
    if not message.strip():
        return history, "", ""
    
    if history is None:
        history = []
    
    if not state.backend_connected:
        check_backend_connection()
        if not state.backend_connected:
            history.append([message, "🚫 **Backend Disconnected** - Please start your Phase 5 backend server first."])
            return history, "", ""
    
    try:
        # Send to your quantized LLM backend
        response = requests.post(
            f"{API_BASE}/chat/quantized",
            json={
                "message": message,
                "language": state.current_language,
                "use_context": True,
                "voice_mode": True,
                "max_tokens": 256
            },
            headers={"Authorization": f"Bearer {state.auth_token}"} if state.auth_token else {},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            
            # Show model info if available
            if result.get("model_loaded"):
                model_info = f"🧠 **Quantized AI Response** ({result.get('inference_time', 0)}ms)"
                ai_response = f"{model_info}\n\n{ai_response}"
            
            # Add to conversation history
            history.append([message, ai_response])
            
            # Get TTS text
            tts_text = result.get("tts_text", clean_for_tts(ai_response))
            
            return history, "", tts_text
            
        else:
            error_msg = f"❌ **AI Error** - Status {response.status_code}"
            history.append([message, error_msg])
            return history, "", "Sorry, the AI model encountered an error."
            
    except Exception as e:
        error_msg = f"🚫 **Error:** {str(e)}"
        history.append([message, error_msg])
        return history, "", "Connection issue occurred. Please check the backend."

def upload_document(files) -> str:
    """Upload documents to your Phase 5 backend"""
    if not state.auth_token:
        return "❌ Please log in first"
    
    if not files:
        return "❌ No files selected"
    
    if not state.backend_connected:
        check_backend_connection()
        if not state.backend_connected:
            return "🚫 **Backend Not Connected** - Please start your Phase 5 backend server first."
    
    try:
        uploaded_files = []
        files_list = files if isinstance(files, list) else [files]
        
        for file in files_list:
            if hasattr(file, 'name'):
                filename = file.name
                
                # Read file content
                try:
                    if hasattr(file, 'read'):
                        content = file.read()
                    else:
                        with open(file, 'rb') as f:
                            content = f.read()
                    
                    # Handle different file types
                    if isinstance(content, bytes):
                        try:
                            text_content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            text_content = content.decode('utf-8', errors='ignore')
                    else:
                        text_content = str(content)
                    
                    # Send to backend
                    response = requests.post(
                        f"{API_BASE}/documents",
                        data={
                            "filename": filename,
                            "content": text_content
                        },
                        headers={"Authorization": f"Bearer {state.auth_token}"} if state.auth_token else {},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        uploaded_files.append({
                            "filename": result.get("filename"),
                            "language": result.get("language"),
                            "word_count": result.get("word_count"),
                            "chunks": result.get("chunks_created")
                        })
                    
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
        
        if uploaded_files:
            result_html = "✅ **Documents Uploaded Successfully!**\n\n"
            
            for file_info in uploaded_files:
                result_html += f"""📄 **{file_info['filename']}**
- Language: {file_info.get('language', 'Unknown')}
- Words: {file_info.get('word_count', 0)}
- Chunks: {file_info.get('chunks', 0)} created for RAG

"""
            
            result_html += "🤖 **Your documents are now available for AI Q&A!**"
            return result_html
        else:
            return "❌ Failed to process any files"
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return f"❌ Upload failed: {str(e)}"

def search_documents(query: str) -> str:
    """Search through uploaded documents using your Phase 5 backend"""
    if not state.auth_token:
        return "❌ Please log in first"
    
    if not query.strip():
        return "❌ Please enter a search query"
    
    if not state.backend_connected:
        check_backend_connection()
        if not state.backend_connected:
            return "🚫 **Backend Not Connected** - Please start your Phase 5 backend server first."
    
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
            
            if not results:
                return f"🔍 No results found for: '{query}'\n\nTry uploading some documents first!"
            
            search_output = f"🔍 **Search Results for:** '{query}'\n\n"
            search_output += f"📊 Found {len(results)} matches in {data.get('total_documents', 0)} documents\n\n"
            
            for i, result in enumerate(results, 1):
                search_output += f"**{i}. {result.get('filename', 'Unknown')}** ({result.get('relevance_score', 0)}% match)\n"
                search_output += f"📝 {result.get('content_preview', 'No preview available')}\n\n"
            
            return search_output
        else:
            return f"❌ Search failed: {response.text}"
    
    except Exception as e:
        return f"❌ Search error: {str(e)}"

def clean_for_tts(text: str) -> str:
    """Clean text for text-to-speech"""
    import re
    
    # Remove emojis and special characters
    text = re.sub(r'[🤖🎓🚀📊🧠❌🚫⚡🔥💡🎤🔊📚🌍🐳💾📄🔍🎯]', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'\n+', '. ', text)
    
    # Remove technical jargon for better speech
    text = text.replace('LLM', 'Language Model')
    text = text.replace('API', 'A P I')
    text = text.replace('AI', 'A I')
    text = text.replace('RAG', 'R A G')
    
    return text.strip()

def create_enhanced_interface():
    """Create enhanced interface building on your Phase 5 system"""
    
    # Enhanced CSS - keeping your existing style but improved
    custom_css = """
    .gradio-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .enhanced-card {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin: 15px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }
    
    .voice-btn {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        border: 3px solid white !important;
        border-radius: 50% !important;
        width: 120px !important;
        height: 120px !important;
        font-size: 3em !important;
        color: white !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        margin: 20px auto !important;
        display: block !important;
    }
    
    .voice-btn:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 15px 40px rgba(79, 172, 254, 0.6) !important;
    }
    
    .listening {
        background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        animation: pulse 1.5s infinite !important;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .status-connected {
        color: #4CAF50 !important;
        font-weight: bold !important;
    }
    
    .status-disconnected {
        color: #f44336 !important;
        font-weight: bold !important;
    }
    """
    
    # Enhanced JavaScript for voice - building on your existing system
    voice_js = """
    <script>
    console.log('🚀 Initializing Enhanced Phase 5 Voice System...');
    
    let recognition = null;
    let isListening = false;
    let speechSynthesis = window.speechSynthesis;
    let lastTTSText = '';
    
    function initVoice() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                console.log('🎤 Voice recognition started');
                isListening = true;
                updateVoiceUI('listening');
                updateStatus('🎤 Listening for your question...');
            };
            
            recognition.onresult = function(event) {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                
                if (interimTranscript) {
                    updateStatus('🎤 Hearing: "' + interimTranscript + '"...');
                }
                
                if (finalTranscript) {
                    console.log('🎤 Recognized:', finalTranscript);
                    const confidence = event.results[event.results.length - 1][0].confidence || 0.8;
                    fillMessageInput(finalTranscript);
                    updateStatus('✅ Got it! "' + finalTranscript + '" (Confidence: ' + Math.round(confidence * 100) + '%)');
                }
            };
            
            recognition.onend = function() {
                console.log('🎤 Voice recognition ended');
                isListening = false;
                updateVoiceUI('ready');
                updateStatus('🎤 Click microphone to speak again');
            };
            
            recognition.onerror = function(event) {
                console.error('🚫 Voice error:', event.error);
                isListening = false;
                updateVoiceUI('error');
                let errorMessage = '';
                switch(event.error) {
                    case 'network':
                        errorMessage = '📶 Network issue - Check your connection';
                        break;
                    case 'not-allowed':
                        errorMessage = '🎤 Please allow microphone access';
                        break;
                    case 'no-speech':
                        errorMessage = '🤫 No speech detected - Try speaking louder';
                        break;
                    default:
                        errorMessage = '❌ Voice error: ' + event.error;
                }
                updateStatus(errorMessage);
            };
        } else {
            console.warn('⚠️ Speech recognition not supported');
            updateStatus('❌ Voice not supported - Use Chrome/Edge');
        }
    }
    
    function startVoice() {
        if (!recognition) {
            initVoice();
        }
        
        if (isListening) {
            recognition.stop();
            updateStatus('🛑 Stopping voice recognition...');
        } else {
            recognition.start();
            updateStatus('🎤 Starting voice recognition...');
        }
    }
    
    function fillMessageInput(text) {
        const textareas = document.getElementsByTagName('textarea');
        for (let textarea of textareas) {
            if (textarea.placeholder && 
                (textarea.placeholder.includes('message') || 
                 textarea.placeholder.includes('Ask'))) {
                textarea.value = text;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.focus();
                break;
            }
        }
    }
    
    function updateVoiceUI(state) {
        const btn = document.getElementById('voice-btn');
        if (btn) {
            btn.className = 'voice-btn' + (state === 'listening' ? ' listening' : '');
            if (state === 'listening') {
                btn.textContent = '🔴';
                btn.title = 'Listening... Click to stop';
            } else if (state === 'error') {
                btn.textContent = '❌';
                btn.title = 'Voice error - Click to retry';
            } else {
                btn.textContent = '🎤';
                btn.title = 'Click to start voice input';
            }
        }
    }
    
    function updateStatus(message) {
        const statusElements = document.querySelectorAll('.voice-status');
        statusElements.forEach(element => {
            element.textContent = message;
        });
        console.log('Status:', message);
    }
    
    function speakText(text) {
        if (speechSynthesis && text && text.trim()) {
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            utterance.onstart = () => updateStatus('🔊 AI is speaking...');
            utterance.onend = () => updateStatus('🎤 Click microphone to continue');
            
            speechSynthesis.speak(utterance);
        }
    }
    
    // Auto-speak TTS responses from your backend
    setInterval(function() {
        const ttsElements = document.querySelectorAll('textarea');
        for (let element of ttsElements) {
            if (element.style.display === 'none' && element.value && element.value !== lastTTSText) {
                lastTTSText = element.value;
                if (element.value.length > 10) {
                    speakText(element.value);
                }
                break;
            }
        }
    }, 1500);
    
    // Initialize when page loads
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(initVoice, 1000);
        updateStatus('🎤 Voice system ready - Click microphone to start');
    });
    
    window.startVoice = startVoice;
    </script>
    """
    
    with gr.Blocks(css=custom_css, title="🤖 Quantized LLM Chatbot - Phase 5 Enhanced") as app:
        
        # Header
        gr.HTML("""
        <div class="enhanced-card">
            <h1 style="font-size: 3rem; margin-bottom: 15px; background: linear-gradient(45deg, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;">
                🤖 Quantized LLM Chatbot - Phase 5
            </h1>
            <h2 style="font-size: 1.5rem; opacity: 0.9; margin-bottom: 20px; text-align: center;">
                Enhanced with Working AI Interaction & Document Upload
            </h2>
            <p style="font-size: 1.1rem; opacity: 0.8; text-align: center;">
                🧠 Real Quantized AI • 🎤 Voice Input/Output • 📚 Document RAG • 🔍 Smart Search
            </p>
        </div>
        """)
        
        # Voice Section - Enhanced
        gr.HTML(f"""
        <div class="enhanced-card">
            <h3 style="margin-top: 0; text-align: center;">🎤 Enhanced Voice Interface</h3>
            <button id="voice-btn" class="voice-btn" onclick="startVoice()" title="Click to start voice input">🎤</button>
            <div class="voice-status" style="color: white; font-size: 1.2em; font-weight: 600; text-align: center; margin: 20px;">
                🎤 Voice system ready - Click microphone to start
            </div>
        </div>
        """)
        
        # Connection Status
        connection_status = gr.HTML("""
        <div class="enhanced-card">
            <div style="text-align: center;">
                <div id="connection-status" class="status-disconnected">🔄 Checking backend connection...</div>
            </div>
        </div>
        """)
        
        # Login Section  
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML("<h3>🔐 Connect to Your Phase 5 Backend</h3>")
                with gr.Row():
                    username_input = gr.Textbox(label="Username", placeholder="Enter username")
                    password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                    login_btn = gr.Button("🚀 Connect to AI", variant="primary")
                
                login_status = gr.HTML('<div class="enhanced-card"><p style="color: #4facfe;">Please log in to access your quantized AI backend</p></div>')
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="enhanced-card">
                    <h4 style="color: #4facfe;">🧠 Phase 5 Features</h4>
                    <ul style="color: rgba(255,255,255,0.9); line-height: 1.6;">
                        <li>🤖 <strong>Real Quantized LLM</strong><br>Working AI responses</li>
                        <li>🎤 <strong>Enhanced Voice</strong><br>Speech recognition & TTS</li>
                        <li>📚 <strong>Document RAG</strong><br>Upload & analyze files</li>
                        <li>🔍 <strong>Smart Search</strong><br>Find info across docs</li>
                        <li>⚡ <strong>Fast Inference</strong><br>Optimized quantized models</li>
                    </ul>
                </div>
                """)
        
        # Main Chat Interface
        with gr.Row():
            with gr.Column(scale=3):
                # Chat - Fixed for Gradio 4.7.1
                chatbot = gr.Chatbot(
                    height=500,
                    show_label=False
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        label="💬 Chat with Your Quantized AI", 
                        placeholder="Ask me anything... (or use voice input above)",
                        lines=2,
                        scale=4
                    )
                    language_select = gr.Dropdown(
                        choices=["en", "ta", "hi", "es", "fr", "de"],
                        value="en",
                        label="🌍 Language",
                        scale=1
                    )
                
                with gr.Row():
                    send_btn = gr.Button("🚀 Send to AI", variant="primary", scale=2)
                    voice_chat_btn = gr.Button("🎤 Voice Chat", variant="secondary", scale=1)
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
                
                # Hidden TTS output
                tts_output = gr.Textbox(
                    visible=False,
                    interactive=False
                )
            
            with gr.Column(scale=1):
                # Document Upload Section - Enhanced for Phase 5
                gr.HTML("<h3>📚 Upload Documents to AI</h3>")
                
                file_upload = gr.File(
                    label="📎 Upload Documents",
                    file_types=[".txt", ".md", ".pdf", ".docx"],
                    file_count="multiple"
                )
                upload_btn = gr.Button("📤 Process with AI", variant="primary")
                upload_result = gr.HTML("""
                <div class="enhanced-card">
                    <p>Upload documents to your quantized AI backend for intelligent analysis and Q&A</p>
                </div>
                """)
                
                # Search Section - Enhanced
                gr.HTML("<h3>🔍 AI-Powered Search</h3>")
                search_input = gr.Textbox(
                    label="Search Query",
                    placeholder="Search through your documents..."
                )
                search_btn = gr.Button("🔍 Search with AI", variant="primary")
                search_results = gr.HTML("""
                <div class="enhanced-card">
                    <p>Search results from your AI backend will appear here</p>
                </div>
                """)
        
        # JavaScript
        gr.HTML(voice_js)
        
        # Event handlers
        login_btn.click(login_user, inputs=[username_input, password_input], outputs=[login_status])
        
        send_btn.click(
            chat_with_ai, 
            inputs=[message_input, chatbot], 
            outputs=[chatbot, message_input, tts_output]
        )
        
        voice_chat_btn.click(
            lambda msg, hist: chat_with_ai(msg, hist),
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, tts_output]
        )
        
        message_input.submit(
            chat_with_ai,
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, tts_output]
        )
        
        clear_btn.click(lambda: ([], ""), outputs=[chatbot, message_input])
        
        upload_btn.click(upload_document, inputs=[file_upload], outputs=[upload_result])
        search_btn.click(search_documents, inputs=[search_input], outputs=[search_results])
    
    return app

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced Phase 5 Frontend...")
    
    # Check backend connection on startup
    if check_backend_connection():
        print("✅ Backend connected successfully!")
    else:
        print("⚠️  Backend not connected. Please start your Phase 5 backend first:")
        print("   python enhanced_backend.py")
    
    app = create_enhanced_interface()
    
    try:
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
    except Exception as e:
        logger.error(f"Failed to launch: {e}")
        print(f"❌ Launch error: {e}")
        print("💡 Make sure port 7860 is free")