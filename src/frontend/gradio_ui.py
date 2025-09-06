#!/usr/bin/env python3
"""
AI Study Buddy - WORKING VOICE EDITION (Fixed)
No warnings, working permissions, speech-to-text
"""

import gradio as gr
import requests
import re
import json
import time

# Configuration
API_BASE = "http://localhost:8000"

# Global state
class StudentState:
    def __init__(self):
        self.auth_token = None
        self.username = None
        self.questions_asked = 0
        self.study_session_start = time.time()

state = StudentState()

def student_login(username, password):
    """Student login"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            return "🚫 **Backend Offline** - Please start the server"
        
        auth_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            state.auth_token = data.get("access_token")
            state.username = username
            
            return f"""✅ **Welcome {username}!**

🎓 **Student Dashboard Activated**
🎤 Voice features enabled
🤖 AI tutor ready
📚 Study mode active

**Ready to learn!** 🚀"""
        else:
            return "❌ **Login Failed** - Try: admin / secret"
            
    except Exception as e:
        return f"🚫 **Connection Error** - {str(e)}"

def student_chat(message, history):
    """Student chat with AI"""
    if not state.auth_token:
        if history is None: history = []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "🔐 **Please log in first!** Use: admin / secret"})
        return history, "", ""
    
    if not message.strip():
        return history, "", ""
    
    if history is None: history = []
    
    # Add user message
    history.append({"role": "user", "content": message})
    state.questions_asked += 1
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"message": message, "use_context": True},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("bot_response", "")
            
            # Enhanced response
            enhanced_response = f"""📚 **Study Buddy Response:**

{ai_response}

💡 **Study Tip:** {get_study_tip(message)}

⏱️ **Session:** Question #{state.questions_asked} | {get_session_time()} minutes"""
            
            # Add AI response
            history.append({"role": "assistant", "content": enhanced_response})
            
            # Clean for TTS
            tts_text = clean_for_speech(ai_response)
            
            return history, "", tts_text
            
        else:
            error_msg = f"❌ **AI Error** - Status {response.status_code}"
            history.append({"role": "assistant", "content": error_msg})
            return history, "", "Sorry, I encountered an error. Please try again."
            
    except Exception as e:
        error_msg = f"🚫 **Error:** {str(e)}"
        history.append({"role": "assistant", "content": error_msg})
        return history, "", "Connection issue occurred. Please check your internet."

def get_study_tip(message):
    """Generate study tips"""
    tips = {
        'math': "Break complex problems into smaller steps",
        'science': "Connect concepts to real-world examples", 
        'history': "Create timeline connections",
        'programming': "Practice coding daily",
        'language': "Immerse yourself in the language daily"
    }
    
    message_lower = message.lower()
    for subject, tip in tips.items():
        if subject in message_lower:
            return tip
    
    return "Take breaks every 25 minutes for better focus"

def get_session_time():
    """Get session duration in minutes"""
    return int((time.time() - state.study_session_start) / 60)

def clean_for_speech(text):
    """Clean text for TTS"""
    # Remove emojis and markdown
    text = re.sub(r'[📚🤖💡⏱️✅❌🚫🎓🎤📊🔥⚡🎯]', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'\n+', '. ', text)
    text = text.replace('AI', 'A I').strip()
    return text

# Create working voice interface
def create_student_interface():
    """Create interface with working voice"""
    
    # Dark theme
    student_theme = gr.themes.Monochrome(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.purple,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
    ).set(
        body_background_fill="#0a0a0a",
        body_text_color="#ffffff",
        block_background_fill="#1a1a2e",
        block_border_color="#16213e",
        block_label_text_color="#ffffff",
        button_primary_background_fill="#4a90e2",
        input_background_fill="#1a1a2e"
    )
    
    # CSS
    student_css = """
        .gradio-container {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%) !important;
            color: #ffffff !important;
        }
        
        .student-header {
            background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%) !important;
            padding: 30px !important;
            border-radius: 20px !important;
            text-align: center !important;
            color: white !important;
            margin-bottom: 30px !important;
            box-shadow: 0 10px 30px rgba(74, 144, 226, 0.3) !important;
        }
        
        .voice-container {
            background: rgba(26, 26, 46, 0.8) !important;
            padding: 30px !important;
            border-radius: 20px !important;
            text-align: center !important;
            margin: 20px 0 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        .voice-btn {
            background: linear-gradient(145deg, #4a90e2, #357abd) !important;
            border: 3px solid #ffffff !important;
            border-radius: 50% !important;
            width: 120px !important;
            height: 120px !important;
            font-size: 3em !important;
            color: white !important;
            cursor: pointer !important;
            margin: 20px auto !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 10px 30px rgba(74, 144, 226, 0.5) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        .voice-btn:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 15px 40px rgba(74, 144, 226, 0.7) !important;
        }
        
        .listening {
            background: linear-gradient(145deg, #4CAF50, #45a049) !important;
            animation: pulse 1.5s infinite !important;
            border-color: #00ff00 !important;
        }
        
        @keyframes pulse {
            0%, 100% { 
                transform: scale(1);
                box-shadow: 0 10px 30px rgba(76, 175, 80, 0.5);
            }
            50% { 
                transform: scale(1.05);
                box-shadow: 0 15px 40px rgba(76, 175, 80, 0.8);
            }
        }
        
        .permission-denied {
            background: linear-gradient(145deg, #f44336, #d32f2f) !important;
            border-color: #ff0000 !important;
        }
        
        .voice-status {
            color: #ffffff !important;
            font-size: 1.2em !important;
            font-weight: 600 !important;
            margin: 20px 0 !important;
            min-height: 50px !important;
        }
        
        .student-card {
            background: rgba(26, 26, 46, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            padding: 25px !important;
            margin: 15px 0 !important;
        }
        
        .student-btn {
            background: linear-gradient(145deg, #4a90e2, #357abd) !important;
            border: none !important;
            border-radius: 10px !important;
            color: white !important;
            padding: 12px 24px !important;
            font-weight: 500 !important;
        }
        
        .student-input {
            background: rgba(26, 26, 46, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: white !important;
        }
    """
    
    with gr.Blocks(theme=student_theme, css=student_css, title="🎤 AI Study Buddy - Working Voice") as app:
        
        # Header
        gr.HTML("""
        <div class="student-header">
            <h1 style="font-size: 2.5rem; margin: 0 0 10px 0;">🎤 AI Study Buddy</h1>
            <h2 style="font-size: 1.5rem; margin: 0 0 15px 0;">Working Voice Edition</h2>
            <p style="font-size: 1.1em; margin: 0;">🎤 Voice Input • 🔊 Text-to-Speech • 🚫 Zero Errors</p>
        </div>
        """)
        
        # Login
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML('<h3 style="color: #4a90e2;">🔐 Student Login</h3>')
                
                with gr.Row():
                    username = gr.Textbox(label="Username", placeholder="admin", elem_classes=["student-input"], scale=2)
                    password = gr.Textbox(label="Password", placeholder="secret", type="password", elem_classes=["student-input"], scale=2)
                    login_btn = gr.Button("🚀 Login", variant="primary", elem_classes=["student-btn"], scale=1)
                
                login_status = gr.Textbox(
                    label="Status",
                    value="Please log in to start your study session",
                    interactive=False,
                    elem_classes=["student-input"]
                )
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="student-card">
                    <h4 style="color: #4a90e2;">🎯 Quick Start</h4>
                    <p><strong>Demo Login:</strong><br>Username: <code>admin</code><br>Password: <code>secret</code></p>
                    <p style="font-size: 0.9em; color: #cccccc;">Get access to voice chat and AI tutoring</p>
                </div>
                """)
        
        # WORKING VOICE SECTION
        gr.HTML('<h3 style="color: #4a90e2; text-align: center; margin: 30px 0 20px 0;">🎤 Voice Input - Click & Speak</h3>')
        
        gr.HTML("""
        <div class="voice-container">
            <div id="permission-info" style="background: rgba(255, 152, 0, 0.1); border: 1px solid rgba(255, 152, 0, 0.3); border-radius: 10px; padding: 15px; margin: 15px 0; color: #ffab00; display: none;">
                <strong>🎤 Microphone Permission Needed</strong><br>
                Click "Allow" when your browser asks for microphone access.
            </div>
            
            <button id="voiceBtn" class="voice-btn" onclick="startVoiceInput()" title="Click to start voice input">
                🎤
            </button>
            
            <div id="voiceStatus" class="voice-status">
                Click the microphone to start voice input
            </div>
            
            <div style="margin-top: 20px; font-size: 0.9em; color: #cccccc;">
                <strong>🌐 Browser Support:</strong><br>
                ✅ Chrome (Recommended) • ✅ Edge (Good) • ⚠️ Safari (Limited) • ❌ Firefox (Not supported)
            </div>
            
            <div style="margin-top: 15px;">
                <button onclick="testMicrophone()" style="background: #ff9800; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; margin-right: 10px;">
                    🔧 Test Microphone
                </button>
                <button onclick="requestPermission()" style="background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer;">
                    🛡️ Request Permission
                </button>
            </div>
        </div>
        """)
        
        # Input and controls
        voice_input = gr.Textbox(
            label="💬 Voice Input / Type Here",
            placeholder="Speak using the microphone above, or type your question here...",
            lines=3,
            elem_classes=["student-input"]
        )
        
        with gr.Row():
            send_btn = gr.Button("🚀 Ask AI", variant="primary", elem_classes=["student-btn"], scale=2)
            speak_btn = gr.Button("🔊 Speak Response", variant="secondary", elem_classes=["student-btn"], scale=1)
            clear_btn = gr.Button("🗑️ Clear", variant="secondary", elem_classes=["student-btn"], scale=1)
        
        # Fixed chatbot (no deprecation warning)
        chatbot = gr.Chatbot(
            height=500,
            type="messages",  # Fixed: using new format
            show_label=False
        )
        
        # TTS output
        tts_output = gr.Textbox(
            label="🔊 Text-to-Speech Output",
            interactive=False,
            lines=2,
            elem_classes=["student-input"]
        )
        
        # WORKING JAVASCRIPT WITH PROPER PERMISSIONS
        gr.HTML("""
        <script>
        console.log('🎤 Loading Voice System...');
        
        let recognition = null;
        let isListening = false;
        let speechSynthesis = window.speechSynthesis;
        let lastTTSText = '';
        let micPermission = 'prompt';
        
        // Check microphone permission
        async function checkPermission() {
            try {
                if (navigator.permissions) {
                    const permission = await navigator.permissions.query({ name: 'microphone' });
                    micPermission = permission.state;
                    console.log('🎤 Microphone permission:', permission.state);
                    updateUI();
                } else {
                    console.log('🎤 Permissions API not supported');
                }
            } catch (error) {
                console.error('🎤 Permission check error:', error);
            }
        }
        
        // Update UI based on permission
        function updateUI() {
            const permissionInfo = document.getElementById('permission-info');
            const voiceBtn = document.getElementById('voiceBtn');
            const voiceStatus = document.getElementById('voiceStatus');
            
            if (micPermission === 'denied') {
                permissionInfo.style.display = 'block';
                permissionInfo.innerHTML = `
                    <strong>❌ Microphone Access Denied</strong><br>
                    Please click the 🔒 icon in your browser's address bar and allow microphone access.
                `;
                voiceBtn.classList.add('permission-denied');
                voiceStatus.innerHTML = '❌ Microphone access denied';
            } else if (micPermission === 'granted') {
                permissionInfo.style.display = 'none';
                voiceBtn.classList.remove('permission-denied');
                if (!isListening) {
                    voiceStatus.innerHTML = '✅ Ready! Click microphone to speak';
                }
            } else {
                permissionInfo.style.display = 'block';
                voiceStatus.innerHTML = 'Click microphone and allow permission';
            }
        }
        
        // Request microphone permission
        async function requestPermission() {
            try {
                console.log('🛡️ Requesting microphone permission...');
                document.getElementById('voiceStatus').innerHTML = '🛡️ Requesting permission...';
                
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                console.log('✅ Permission granted');
                
                // Stop stream immediately
                stream.getTracks().forEach(track => track.stop());
                
                micPermission = 'granted';
                updateUI();
                initSpeechRecognition();
                
            } catch (error) {
                console.error('❌ Permission denied:', error);
                micPermission = 'denied';
                updateUI();
            }
        }
        
        // Test microphone
        async function testMicrophone() {
            try {
                console.log('🔧 Testing microphone...');
                document.getElementById('voiceStatus').innerHTML = '🔧 Testing microphone...';
                
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                console.log('✅ Microphone test passed');
                
                setTimeout(() => {
                    stream.getTracks().forEach(track => track.stop());
                    document.getElementById('voiceStatus').innerHTML = '✅ Test passed! Ready for voice input';
                }, 2000);
                
            } catch (error) {
                console.error('❌ Test failed:', error);
                document.getElementById('voiceStatus').innerHTML = '❌ Test failed: ' + error.message;
            }
        }
        
        // Initialize speech recognition
        function initSpeechRecognition() {
            if ('webkitSpeechRecognition' in window) {
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                recognition.onstart = function() {
                    console.log('🎤 Speech recognition started');
                    isListening = true;
                    document.getElementById('voiceBtn').classList.add('listening');
                    document.getElementById('voiceStatus').innerHTML = '🎤 <strong style="color: #4CAF50;">LISTENING...</strong><br>Speak clearly now!';
                };
                
                recognition.onresult = function(event) {
                    let finalTranscript = '';
                    let interimTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        let transcript = event.results[i][0].transcript;
                        
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    
                    if (interimTranscript) {
                        document.getElementById('voiceStatus').innerHTML = 
                            '🎤 <strong style="color: #ff9800;">Hearing:</strong><br>"' + interimTranscript + '"';
                    }
                    
                    if (finalTranscript) {
                        console.log('🎤 Final:', finalTranscript);
                        fillTextInput(finalTranscript);
                        document.getElementById('voiceStatus').innerHTML = 
                            '✅ <strong style="color: #4CAF50;">Got it!</strong><br>"' + finalTranscript.substring(0, 50) + 
                            (finalTranscript.length > 50 ? '..."' : '"');
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('🚫 Speech error:', event.error);
                    isListening = false;
                    document.getElementById('voiceBtn').classList.remove('listening');
                    
                    let errorMsg = '❌ Error: ';
                    switch(event.error) {
                        case 'not-allowed':
                            errorMsg += 'Microphone permission denied';
                            micPermission = 'denied';
                            updateUI();
                            return;
                        case 'no-speech':
                            errorMsg += 'No speech detected. Try speaking louder.';
                            break;
                        case 'audio-capture':
                            errorMsg += 'Microphone not found';
                            break;
                        case 'network':
                            errorMsg += 'Network error';
                            break;
                        default:
                            errorMsg += event.error;
                    }
                    
                    document.getElementById('voiceStatus').innerHTML = errorMsg;
                    
                    setTimeout(() => {
                        if (micPermission === 'granted') {
                            document.getElementById('voiceStatus').innerHTML = 'Click microphone to try again';
                        }
                    }, 3000);
                };
                
                recognition.onend = function() {
                    console.log('🎤 Speech ended');
                    isListening = false;
                    document.getElementById('voiceBtn').classList.remove('listening');
                    
                    const currentStatus = document.getElementById('voiceStatus').innerHTML;
                    if (currentStatus.includes('LISTENING') || currentStatus === '') {
                        document.getElementById('voiceStatus').innerHTML = 'Click microphone to speak again';
                    }
                };
                
                console.log('✅ Speech recognition ready');
                return true;
            } else {
                document.getElementById('voiceStatus').innerHTML = 
                    '❌ Voice not supported in this browser.<br>Please use Chrome or Edge.';
                return false;
            }
        }
        
        // Fill text input
        function fillTextInput(text) {
            const textareas = document.getElementsByTagName('textarea');
            for (let textarea of textareas) {
                if (textarea.placeholder && textarea.placeholder.includes('Voice Input')) {
                    textarea.value = text;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    textarea.focus();
                    break;
                }
            }
        }
        
        // Start voice input
        async function startVoiceInput() {
            console.log('🎤 Starting voice input...');
            
            if (isListening && recognition) {
                console.log('🛑 Stopping');
                recognition.stop();
                return;
            }
            
            if (micPermission !== 'granted') {
                await requestPermission();
                if (micPermission === 'denied') return;
            }
            
            if (!recognition) {
                if (!initSpeechRecognition()) return;
            }
            
            try {
                console.log('🎤 Starting recognition...');
                recognition.start();
            } catch (error) {
                console.error('🚫 Start error:', error);
                document.getElementById('voiceStatus').innerHTML = '❌ Failed to start: ' + error.message;
            }
        }
        
        // Text-to-speech
        function speakText(text) {
            if (!text || !speechSynthesis) return;
            
            console.log('🔊 Speaking:', text.substring(0, 50) + '...');
            
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.85;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            const voices = speechSynthesis.getVoices();
            const englishVoice = voices.find(voice => 
                voice.lang.startsWith('en') && 
                (voice.name.includes('Google') || voice.name.includes('Microsoft') || voice.default)
            );
            
            if (englishVoice) {
                utterance.voice = englishVoice;
                console.log('🔊 Using voice:', englishVoice.name);
            }
            
            utterance.onstart = function() {
                document.getElementById('voiceStatus').innerHTML = '🔊 <strong style="color: #2196F3;">Speaking AI response...</strong>';
            };
            
            utterance.onend = function() {
                document.getElementById('voiceStatus').innerHTML = 'Click microphone for another question';
            };
            
            speechSynthesis.speak(utterance);
        }
        
        // Monitor for TTS updates
        function monitorTTS() {
            const ttsElements = document.querySelectorAll('textarea');
            
            for (let element of ttsElements) {
                const label = element.parentElement?.previousElementSibling?.textContent || '';
                
                if (label.includes('Text-to-Speech Output') && element.value && 
                    element.value !== lastTTSText && element.value.length > 10) {
                    
                    lastTTSText = element.value;
                    console.log('🔊 Auto-speaking...');
                    setTimeout(() => speakText(element.value), 1500);
                    break;
                }
            }
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', async function() {
            console.log('🎤 Initializing Voice System...');
            
            await checkPermission();
            
            if (speechSynthesis) {
                speechSynthesis.onvoiceschanged = function() {
                    console.log('🔊 Voices loaded:', speechSynthesis.getVoices().length);
                };
                speechSynthesis.getVoices();
            }
            
            setInterval(monitorTTS, 2000);
            
            console.log('✅ Voice system ready!');
        });
        
        // Global functions
        window.startVoiceInput = startVoiceInput;
        window.requestPermission = requestPermission;
        window.testMicrophone = testMicrophone;
        window.speakText = speakText;
        </script>
        """)
        
        # Footer
        gr.HTML("""
        <div class="student-header" style="margin-top: 40px;">
            <h3>🎤 AI Study Buddy - Working Voice Edition</h3>
            <p style="opacity: 0.8;">✅ No warnings • ✅ Working voice • ✅ Proper permissions • ✅ Auto TTS</p>
            <p style="font-size: 0.9em; opacity: 0.6; margin: 10px 0 0 0;">
                Built by: Muthukkumaran S, Surya S, Shiva Raj Ganesh N S
            </p>
        </div>
        """)
        
        # Event handlers (fixed for new message format)
        def handle_chat(message, history):
            result = student_chat(message, history)
            if state.auth_token and message.strip():
                gr.Info(f"Question #{state.questions_asked} - Keep learning! 🚀")
            return result
        
        def handle_speak_response(history):
            if history and len(history) > 0:
                # Handle new message format
                last_message = history[-1]
                if isinstance(last_message, dict) and 'content' in last_message:
                    return clean_for_speech(last_message['content'])
                elif isinstance(last_message, list) and len(last_message) > 1:
                    return clean_for_speech(last_message[1])
            return "No response to speak"
        
        # Connect events
        login_btn.click(student_login, inputs=[username, password], outputs=[login_status])
        
        send_btn.click(handle_chat, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, tts_output])
        voice_input.submit(handle_chat, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, tts_output])
        
        speak_btn.click(handle_speak_response, inputs=[chatbot], outputs=[tts_output])
        
        clear_btn.click(lambda: ([], ""), outputs=[chatbot, voice_input])
    
    return app

# Launch with different port if needed
if __name__ == "__main__":
    print("🎤" + "="*60)
    print("  AI STUDY BUDDY - FIXED VOICE EDITION")
    print("  ✅ No Warnings • ✅ Working Voice • ✅ Permissions")
    print("🎤" + "="*60)
    print("")
    print("🔧 Fixed Issues:")
    print("  ✅ Port conflict resolved")
    print("  ✅ Chatbot deprecation warning fixed")
    print("  ✅ Proper microphone permissions")
    print("  ✅ Working speech-to-text")
    print("  ✅ Automatic text-to-speech")
    print("")
    print("🚀 Launch: http://localhost:7860")
    print("🎤" + "="*60)
    
    app = create_student_interface()
    
    # Try different ports if 7860 is busy
    for port in [7860, 7861, 7862, 7863]:
        try:
            app.launch(server_name="0.0.0.0", server_port=port, share=False)
            print(f"✅ Launched on port {port}")
            break
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Port {port} busy, trying next...")
                continue
            else:
                raise e
