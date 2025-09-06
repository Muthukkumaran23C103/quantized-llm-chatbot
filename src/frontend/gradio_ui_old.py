#!/usr/bin/env python3
"""AI Study Buddy - Voice Interface (Alexa-Style)"""

import gradio as gr
import requests
import re

# Global variables
auth_token = None
API_BASE = "http://localhost:8000"

def login_user(user, pwd):
    global auth_token
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={"username": user, "password": pwd}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            return f"✅ Welcome {user}! Voice assistant activated! 🎤"
        else:
            return "❌ Invalid credentials. Try: admin / secret"
    except:
        return "🚫 Connection error"

def logout_user():
    global auth_token
    auth_token = None
    return "👋 Logged out! Voice assistant deactivated."

def clean_text_for_speech(text):
    """Clean text for better TTS"""
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

def chat_with_voice(message, history):
    global auth_token
    
    if not auth_token:
        if history is None: history = []
        response_msg = "🔐 Please log in first! Use admin / secret"
        history.append([message, response_msg])
        return history, "", response_msg
    
    if not message.strip():
        return history, "", ""
    
    if history is None: history = []
    
    history.append([message, "🤖 AI thinking... 🎤"])
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"message": message, "use_context": True, "voice_mode": True},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("bot_response", "No response")
            voice_response = result.get("voice_response", "")
            
            ai_response += "\n\n🔊 *Auto-speaking enabled*"
            history[-1][1] = ai_response
            
            return history, "", voice_response
        else:
            error_msg = f"❌ Error {response.status_code}"
            history[-1][1] = error_msg
            return history, "", "Sorry, I encountered an error."
            
    except Exception as e:
        error_msg = f"🚫 Error: {str(e)}"
        history[-1][1] = error_msg
        return history, "", "Sorry, connection issue."

# Create interface
with gr.Blocks(title="🎤 AI Study Buddy - Voice Assistant") as app:
    
    gr.HTML("""
    <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 20px;'>
        <h1>🎤 AI Study Buddy - Voice Assistant</h1>
        <h2>✨ Alexa-Style Education Helper ✨</h2>
        <p><strong>Say "Hey Study Buddy" to activate voice!</strong></p>
        <p>🔊 Text-to-Speech • 🎤 Voice Recognition • 🧠 AI Intelligence</p>
        <p><strong>Team:</strong> Muthukkumaran S, Surya S, Shiva Raj Ganesh N S</p>
    </div>
    """)
    
    # Login
    gr.HTML("<h2>🔐 Login First</h2>")
    with gr.Row():
        user_input = gr.Textbox(label="Username", placeholder="admin", scale=2)
        pwd_input = gr.Textbox(label="Password", placeholder="secret", type="password", scale=2)
        login_btn = gr.Button("🔐 Login", variant="primary", scale=1)
        logout_btn = gr.Button("👋 Logout", variant="secondary", scale=1)
    
    status_box = gr.Textbox(label="Status", value="Please log in: admin / secret", interactive=False)
    
    # Voice Control
    gr.HTML("<h2>🎤 Voice Control Center</h2>")
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 15px; margin: 10px 0;">
        <h3>🎤 Click to Start Listening</h3>
        <button id="voice-btn" onclick="toggleVoice()" style="background: linear-gradient(45deg, #ff6b6b, #ee5a24); border: none; border-radius: 50%; width: 80px; height: 80px; font-size: 2em; color: white; cursor: pointer;">🎤</button>
        <p id="voice-status">Click microphone to start</p>
        <p><strong>Try:</strong> "Hey Study Buddy, help me with math"</p>
    </div>
    """)
    
    voice_input = gr.Textbox(
        label="Voice Input (or type here)",
        placeholder="Say 'Hey Study Buddy, explain photosynthesis' or type your question..."
    )
    
    with gr.Row():
        send_btn = gr.Button("🚀 Send", variant="primary", scale=2)
        speak_btn = gr.Button("🔊 Speak", variant="secondary", scale=1)
        clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
    
    # Chat
    gr.HTML("<h2>💬 Voice Chat</h2>")
    chatbot = gr.Chatbot(height=400, type="tuples")
    
    # Hidden TTS output
    tts_output = gr.Textbox(visible=False)
    
    # Voice JavaScript
    gr.HTML("""
    <script>
    let recognition;
    let isListening = false;
    
    function initVoice() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                document.getElementById('voice-status').textContent = '🎤 Listening... Say something!';
                document.getElementById('voice-btn').style.background = 'linear-gradient(45deg, #00ff00, #32cd32)';
            };
            
            recognition.onresult = function(event) {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                
                if (finalTranscript) {
                    const voiceInput = document.querySelector('textarea[placeholder*="Say"]');
                    if (voiceInput) {
                        voiceInput.value = finalTranscript;
                        voiceInput.dispatchEvent(new Event('input'));
                    }
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('voice-status').textContent = '❌ Error: ' + event.error;
                document.getElementById('voice-btn').style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
                isListening = false;
            };
            
            recognition.onend = function() {
                document.getElementById('voice-status').textContent = 'Click microphone to start';
                document.getElementById('voice-btn').style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
                isListening = false;
            };
        }
    }
    
    function toggleVoice() {
        if (!recognition) initVoice();
        
        if (isListening) {
            recognition.stop();
            isListening = false;
        } else {
            recognition.start();
            isListening = true;
        }
    }
    
    function speakText(text) {
        if (!text || !window.speechSynthesis) return;
        
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(voice => voice.lang.includes('en'));
        if (englishVoice) utterance.voice = englishVoice;
        
        utterance.onstart = function() {
            document.getElementById('voice-status').textContent = '🔊 Speaking...';
        };
        
        utterance.onend = function() {
            document.getElementById('voice-status').textContent = 'Click microphone to start';
        };
        
        window.speechSynthesis.speak(utterance);
    }
    
    // Auto-speak when TTS output changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            const ttsElements = document.querySelectorAll('textarea');
            ttsElements.forEach(function(element) {
                if (element.value && element.value.length > 10 && element.parentElement.style.display !== 'none') {
                    if (element.value !== element.dataset.lastValue) {
                        element.dataset.lastValue = element.value;
                        setTimeout(() => speakText(element.value), 500);
                    }
                }
            });
        });
    });
    
    document.addEventListener('DOMContentLoaded', function() {
        initVoice();
        observer.observe(document.body, { childList: true, subtree: true });
    });
    
    window.toggleVoice = toggleVoice;
    window.speakText = speakText;
    </script>
    """)
    
    # Voice commands help
    gr.HTML("""
    <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin-top: 20px;'>
        <h3>🗣️ Voice Commands:</h3>
        <ul style='text-align: left; display: inline-block;'>
            <li>"Hey Study Buddy, explain [topic]"</li>
            <li>"Help me with [subject]"</li>
            <li>"What is [concept]?"</li>
            <li>"Give me study tips"</li>
            <li>"Login" / "Logout"</li>
        </ul>
        <h3>🎯 Perfect for Students!</h3>
        <p>Hands-free learning • Audio responses • Natural conversation</p>
    </div>
    """)
    
    # Event handlers
    def handle_voice_chat(message, history):
        return chat_with_voice(message, history)
    
    def handle_speak_response(history):
        if history and len(history) > 0:
            last_response = history[-1][1] if len(history[-1]) > 1 else ""
            return clean_text_for_speech(last_response)
        return ""
    
    login_btn.click(login_user, inputs=[user_input, pwd_input], outputs=[status_box])
    logout_btn.click(logout_user, outputs=[status_box])
    
    send_btn.click(handle_voice_chat, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, tts_output])
    voice_input.submit(handle_voice_chat, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, tts_output])
    
    speak_btn.click(handle_speak_response, inputs=[chatbot], outputs=[tts_output])
    clear_btn.click(lambda: [], outputs=[chatbot])

print("🎤 AI Study Buddy - Voice Assistant Starting!")
print("✨ Features: Voice Recognition + TTS + AI Chat")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
