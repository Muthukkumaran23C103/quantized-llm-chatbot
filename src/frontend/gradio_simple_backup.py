#!/usr/bin/env python3
"""AI Study Buddy - Beautiful Voice Interface"""

import gradio as gr
import requests
import re

# Global variables
auth_token = None
API_BASE = "http://localhost:8000"

def test_backend():
    """Test backend connection"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            return "✅ Backend connected and healthy"
        else:
            return f"❌ Backend error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "🚫 Backend not running - Please start: cd src/api && python main.py"
    except Exception as e:
        return f"🚫 Connection error: {str(e)}"

def login_user(user, pwd):
    """Login with connection test"""
    global auth_token
    
    # Test connection first
    conn_status = test_backend()
    if "🚫" in conn_status or "❌" in conn_status:
        return conn_status
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={"username": user, "password": pwd}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            return f"✅ Welcome {user}! 🎤 Voice assistant activated!"
        else:
            return "❌ Invalid credentials. Try: admin / secret"
    except Exception as e:
        return f"🚫 Login error: {str(e)}"

def logout_user():
    global auth_token
    auth_token = None
    return "👋 Logged out! Voice assistant deactivated."

def clean_for_speech(text):
    """Clean text for TTS"""
    if not text:
        return ""
    
    # Remove markdown and emojis
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'[🤖🎓📚💡🔧⚡🎯📄🔍✅❌🚫👋🎤🔊🌟✨📊🏥🚀🎉]', '', text)
    
    # Replace abbreviations
    text = text.replace('AI', 'Artificial Intelligence')
    text = text.replace('API', 'A P I')
    text = text.replace('&', 'and')
    text = text.replace('vs', 'versus')
    
    # Clean formatting
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\*.*?\*', '', text)
    
    return text.strip()

def chat_with_ai(message, history):
    """Enhanced chat with error handling"""
    global auth_token
    
    if not auth_token:
        if history is None: history = []
        response_msg = "🔐 Please log in first! Use: admin / secret"
        history.append([message, response_msg])
        return history, "", response_msg
    
    if not message.strip():
        return history, "", ""
    
    if history is None: history = []
    
    history.append([message, "🤖 AI is thinking... 💭"])
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"message": message, "use_context": True, "voice_mode": True},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("bot_response", "")
            
            # Clean for TTS
            voice_text = clean_for_speech(ai_response)
            
            # Add voice indicator
            ai_response += "\n\n🔊 *Auto-speaking enabled*"
            history[-1][1] = ai_response
            
            return history, "", voice_text
        else:
            error_msg = f"❌ API Error {response.status_code}"
            history[-1][1] = error_msg
            return history, "", "Sorry, I encountered an error."
            
    except requests.exceptions.ConnectionError:
        error_msg = "🚫 Lost connection to backend!"
        history[-1][1] = error_msg
        return history, "", "Sorry, connection to the backend was lost."
        
    except Exception as e:
        error_msg = f"🚫 Error: {str(e)}"
        history[-1][1] = error_msg
        return history, "", "Sorry, an unexpected error occurred."

def upload_file(file):
    """File upload handler"""
    global auth_token
    
    if not auth_token:
        return "🔐 Please log in first!"
    
    if file is None:
        return "📄 Please select a file."
    
    try:
        content = file.read() if hasattr(file, 'read') else open(file, 'r').read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        
        filename = file.name if hasattr(file, 'name') else 'document.txt'
        
        response = requests.post(
            f"{API_BASE}/documents",
            json={"filename": filename, "content": content, "metadata": {}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get("analysis", {})
            return f"""✅ **Document Uploaded Successfully!**

📄 **File:** {filename}
📊 **Analysis:**
• Word Count: {analysis.get('word_count', 0)}
• Status: {analysis.get('status', 'processed')}

💡 Now you can ask me questions about this document!"""
        else:
            return f"❌ Upload failed: HTTP {response.status_code}"
            
    except Exception as e:
        return f"🚫 Upload error: {str(e)}"

# Create beautiful Gradio interface
with gr.Blocks(
    title="🎤 AI Study Buddy - Beautiful Voice Assistant",
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.purple,
        font=[gr.themes.GoogleFont("Inter"), "Arial", "sans-serif"]
    ),
    css="""
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .main-header { 
            text-align: center; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 25px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.15) !important;
            padding: 25px !important;
            border-radius: 20px !important;
            margin: 15px 0 !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: transform 0.3s ease !important;
        }
        .feature-card:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1) !important;
        }
        .voice-button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24) !important;
            border: none !important;
            border-radius: 50% !important;
            width: 120px !important;
            height: 120px !important;
            font-size: 3em !important;
            color: white !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            margin: 20px !important;
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3) !important;
        }
        .voice-button:hover {
            transform: scale(1.1) !important;
        }
        .listening {
            background: linear-gradient(45deg, #00ff00, #32cd32) !important;
            animation: pulse 1.5s infinite !important;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .gradio-container {
            background: transparent !important;
        }
        .block {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 15px !important;
        }
    """
) as demo:
    
    # Beautiful Header
    gr.HTML("""
    <div class="main-header">
        <h1 style="font-size: 3.5rem; margin: 0 0 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🎤 AI Study Buddy</h1>
        <h2 style="font-size: 2rem; margin: 0 0 20px 0; opacity: 0.9;">Beautiful Voice Assistant ✨</h2>
        <p style="font-size: 1.3em; margin: 0 0 10px 0;"><strong>🔊 Text-to-Speech • 🎤 Voice Recognition • 🧠 AI Intelligence</strong></p>
        <p style="font-size: 1.1em; opacity: 0.8; margin: 0;"><strong>Team:</strong> Muthukkumaran S, Surya S, Shiva Raj Ganesh N S</p>
        <p style="font-size: 1.1em; opacity: 0.8; margin: 5px 0 0 0;"><strong>Institution:</strong> Thiagarajar College of Engineering - GLUGOT</p>
    </div>
    """)
    
    # Connection Status
    with gr.Row():
        connection_status = gr.Textbox(
            label="🔌 Backend Status",
            value="Testing connection...",
            interactive=False
        )
        test_conn_btn = gr.Button("🔄 Test Connection", variant="secondary")
    
    # Login Section
    gr.HTML('<h2 style="text-align: center; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🔐 Authentication</h2>')
    
    with gr.Row():
        with gr.Column(scale=3):
            with gr.Row():
                username = gr.Textbox(label="👤 Username", placeholder="admin", scale=2)
                password = gr.Textbox(label="🔑 Password", placeholder="secret", type="password", scale=2)
                login_btn = gr.Button("🔐 Login", variant="primary", scale=1)
                logout_btn = gr.Button("👋 Logout", variant="secondary", scale=1)
            
            login_status = gr.Textbox(
                label="🚦 Status",
                value="Please log in to activate voice features",
                interactive=False
            )
        
        with gr.Column(scale=1):
            gr.HTML("""
            <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 15px; color: white; text-align: center;">
                <h3 style="margin-top: 0;">🎯 Demo Credentials</h3>
                <p><strong>Admin:</strong> admin / secret</p>
                <p><strong>User:</strong> user1 / secret</p>
            </div>
            """)
    
    # Voice Control
    gr.HTML('<h2 style="text-align: center; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🎤 Voice Control Center</h2>')
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
            <div style="text-align: center; padding: 30px; background: rgba(255,255,255,0.2); border-radius: 20px; margin: 10px;">
                <h3 style="color: white; margin: 0 0 20px 0;">🎤 Voice Input</h3>
                <button id="voiceBtn" onclick="toggleVoice()" class="voice-button">🎤</button>
                <div id="voiceStatus" style="color: white; margin: 20px 0; font-weight: bold;">
                    Click microphone to start
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.9em;">
                    <strong>Browser Support:</strong><br>
                    ✅ Chrome/Edge<br>⚠️ Safari<br>❌ Firefox
                </div>
            </div>
            """)
            
        with gr.Column(scale=2):
            voice_input = gr.Textbox(
                label="🗣️ Voice Input / Text Input",
                placeholder="Voice input will appear here, or type your message...",
                lines=3
            )
            
            with gr.Row():
                send_btn = gr.Button("🚀 Send Message", variant="primary", scale=3)
                speak_btn = gr.Button("🔊 Speak Response", variant="secondary", scale=2)
                clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
    
    # Chat Interface
    gr.HTML('<h2 style="text-align: center; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">💬 AI Chat</h2>')
    
    chatbot = gr.Chatbot(
        height=500,
        type="tuples",
        show_label=True,
        container=True
    )
    
    # TTS Output
    tts_output = gr.Textbox(
        label="🔊 TTS Output (Auto-speaking)",
        interactive=False,
        lines=2
    )
    
    # File Upload Section
    with gr.Tab("📚 Documents"):
        gr.HTML('<h3 style="color: white;">📄 Document Upload & Analysis</h3>')
        
        with gr.Row():
            with gr.Column(scale=2):
                file_input = gr.File(label="📎 Select File", file_types=[".txt", ".md", ".py", ".json"])
                upload_btn = gr.Button("📤 Upload & Analyze", variant="primary")
                upload_result = gr.Textbox(label="📋 Results", lines=8, interactive=False)
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 15px; color: white;">
                    <h4>📚 Features</h4>
                    <ul style="text-align: left;">
                        <li>📝 Text analysis</li>
                        <li>🏷️ Keyword extraction</li>
                        <li>📊 Statistics</li>
                        <li>🔍 Searchable</li>
                    </ul>
                </div>
                """)
    
    # Voice JavaScript
    gr.HTML("""
    <script>
    let recognition;
    let isListening = false;
    let lastTTSText = '';
    
    function initVoice() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                document.getElementById('voiceStatus').innerHTML = '🎤 <span style="color: #ff6b6b;">LISTENING...</span><br>Speak now!';
                document.getElementById('voiceBtn').classList.add('listening');
                isListening = true;
            };
            
            recognition.onresult = function(event) {
                let final = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        final += event.results[i][0].transcript;
                    }
                }
                
                if (final) {
                    const textareas = document.getElementsByTagName('textarea');
                    for (let ta of textareas) {
                        if (ta.placeholder && ta.placeholder.includes('Voice input')) {
                            ta.value = final;
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                    }
                    document.getElementById('voiceStatus').innerHTML = '✅ <span style="color: #00ff00;">Got:</span><br>"' + final.substring(0, 50) + '"';
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('voiceStatus').innerHTML = '❌ Error: ' + event.error;
                document.getElementById('voiceBtn').classList.remove('listening');
                isListening = false;
            };
            
            recognition.onend = function() {
                document.getElementById('voiceBtn').classList.remove('listening');
                isListening = false;
                if (!document.getElementById('voiceStatus').innerHTML.includes('Got:')) {
                    document.getElementById('voiceStatus').innerHTML = 'Click microphone to start';
                }
            };
            
            return true;
        } else {
            document.getElementById('voiceStatus').innerHTML = '❌ Not supported<br>Use Chrome/Edge';
            return false;
        }
    }
    
    function toggleVoice() {
        if (!recognition && !initVoice()) return;
        
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch(e) {
                document.getElementById('voiceStatus').innerHTML = '❌ Error: ' + e.message;
            }
        }
    }
    
    function speakText(text) {
        if (!text || !window.speechSynthesis) return;
        
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(v => v.lang.includes('en'));
        if (englishVoice) utterance.voice = englishVoice;
        
        utterance.onstart = () => document.getElementById('voiceStatus').innerHTML = '🔊 <span style="color: #3498db;">Speaking...</span>';
        utterance.onend = () => document.getElementById('voiceStatus').innerHTML = 'Click microphone to start';
        
        window.speechSynthesis.speak(utterance);
    }
    
    function checkTTSUpdates() {
        const ttsElements = document.getElementsByTagName('textarea');
        for (let el of ttsElements) {
            const label = el.parentElement?.previousElementSibling?.textContent;
            if (label && label.includes('TTS Output') && el.value && el.value !== lastTTSText && el.value.length > 5) {
                lastTTSText = el.value;
                setTimeout(() => speakText(el.value), 1000);
                break;
            }
        }
    }
    
    setInterval(checkTTSUpdates, 2000);
    
    document.addEventListener('DOMContentLoaded', function() {
        initVoice();
        if (window.speechSynthesis) {
            window.speechSynthesis.onvoiceschanged = () => console.log('Voices loaded');
        }
    });
    
    window.toggleVoice = toggleVoice;
    window.speakText = speakText;
    </script>
    """)
    
    # Instructions
    gr.HTML("""
    <div style='background: rgba(255,255,255,0.2); padding: 25px; border-radius: 20px; margin: 20px 0; color: white;'>
        <h3 style='text-align: center; margin-top: 0;'>🎯 How to Use</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;'>
            <div>
                <h4>🔐 1. Login</h4>
                <p>Use: admin / secret</p>
            </div>
            <div>
                <h4>🎤 2. Voice Input</h4>
                <p>Click mic, allow permissions, speak</p>
            </div>
            <div>
                <h4>🚀 3. Send</h4>
                <p>Click "Send Message" after speaking</p>
            </div>
            <div>
                <h4>🔊 4. Listen</h4>
                <p>Response auto-speaks in ~1 second</p>
            </div>
        </div>
    </div>
    """)
    
    # Event handlers
    def handle_speak_response(history):
        if history and len(history) > 0 and len(history[-1]) > 1:
            return clean_for_speech(history[-1][1])
        return "No response to speak"
    
    # Connect events
    test_conn_btn.click(test_backend, outputs=[connection_status])
    
    login_btn.click(login_user, inputs=[username, password], outputs=[login_status])
    logout_btn.click(logout_user, outputs=[login_status])
    
    send_btn.click(chat_with_ai, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, tts_output])
    voice_input.submit(chat_with_ai, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, tts_output])
    
    speak_btn.click(handle_speak_response, inputs=[chatbot], outputs=[tts_output])
    
    upload_btn.click(upload_file, inputs=[file_input], outputs=[upload_result])
    
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, voice_input])

print("🎨 AI Study Buddy - Beautiful Voice Assistant")
print("✨ Features: Beautiful UI + Voice Recognition + Auto-TTS")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, debug=True)
