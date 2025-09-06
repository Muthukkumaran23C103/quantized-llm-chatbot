#!/usr/bin/env python3
"""AI Study Buddy - WORKING Gradio Interface"""

import gradio as gr
import requests

# Global variables - NO CLASSES!
auth_token = None
API_BASE = "http://localhost:8000"

def login_user(user, pwd):
    global auth_token
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={"username": user, "password": pwd}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            return f"✅ Welcome {user}! Login successful!"
        else:
            auth_token = None
            return "❌ Invalid credentials. Try: admin / secret"
    except:
        return "🚫 Connection error"

def chat_ai(message, history):
    global auth_token
    if not auth_token:
        if history is None: history = []
        history.append([message, "🔐 Please log in first! Use: admin / secret"])
        return history, ""
    
    if not message.strip(): return history, ""
    if history is None: history = []
    
    history.append([message, "🤖 AI thinking..."])
    
    try:
        response = requests.post(f"{API_BASE}/chat", json={"message": message, "use_context": True}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("bot_response", "No response")
            history[-1][1] = ai_response
        else:
            history[-1][1] = f"❌ Error {response.status_code}"
    except Exception as e:
        history[-1][1] = f"🚫 Error: {str(e)}"
    
    return history, ""

# Create interface
with gr.Blocks(title="🤖 AI Study Buddy - WORKING!") as app:
    
    gr.HTML("""
    <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white;'>
        <h1>🤖 AI Study Buddy - WORKING VERSION!</h1>
        <p>No Self Errors - Complete AI Integration</p>
    </div>
    """)
    
    # Login
    with gr.Row():
        user_box = gr.Textbox(label="Username", placeholder="admin", scale=2)
        pwd_box = gr.Textbox(label="Password", placeholder="secret", type="password", scale=2)
        login_btn = gr.Button("🔐 Login", variant="primary", scale=1)
    
    status_box = gr.Textbox(label="Status", value="Please log in: admin / secret", interactive=False)
    
    # Chat
    gr.HTML("<h2>💬 AI Chat</h2>")
    chatbot = gr.Chatbot(height=400, type="tuples")
    msg_box = gr.Textbox(label="Message", placeholder="Ask me anything!")
    send_btn = gr.Button("🚀 Send", variant="primary")
    
    # Connect functions
    login_btn.click(login_user, inputs=[user_box, pwd_box], outputs=[status_box])
    send_btn.click(chat_ai, inputs=[msg_box, chatbot], outputs=[chatbot, msg_box])
    msg_box.submit(chat_ai, inputs=[msg_box, chatbot], outputs=[chatbot, msg_box])

if __name__ == "__main__":
    print("🚀 Starting WORKING AI Study Buddy interface...")
    app.launch(server_name="0.0.0.0", server_port=7860)
