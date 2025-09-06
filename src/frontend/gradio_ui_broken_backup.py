import gradio as gr
import requests
import json
import time
import asyncio
from typing import List, Tuple, Optional
import threading

# Configuration
API_BASE = "http://localhost:8000"
STUDENT_THEME_CSS = """
/* Student-friendly modern CSS theme */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Global Styles */
.gradio-container {
    font-family: 'Poppins', sans-serif !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    min-height: 100vh;
}

/* Main container with glassmorphism */
.main-container {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
    margin: 20px !important;
    padding: 30px !important;
    animation: fadeInUp 0.8s ease-out !important;
}

/* Header styling */
.header-text {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    text-align: center !important;
    margin-bottom: 10px !important;
    animation: rainbow 3s ease-in-out infinite alternate !important;
}

.subtitle-text {
    color: rgba(255, 255, 255, 0.9) !important;
    text-align: center !important;
    font-size: 1.2rem !important;
    margin-bottom: 30px !important;
    font-weight: 300 !important;
}

/* Chat interface styling */
.chat-container {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 15px !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    min-height: 400px !important;
    max-height: 600px !important;
}

/* Message bubbles */
.message.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 18px 18px 5px 18px !important;
    padding: 12px 18px !important;
    margin: 10px 0 !important;
    max-width: 80% !important;
    margin-left: auto !important;
    animation: slideInRight 0.3s ease-out !important;
}

.message.bot {
    background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%) !important;
    color: white !important;
    border-radius: 18px 18px 18px 5px !important;
    padding: 12px 18px !important;
    margin: 10px 0 !important;
    max-width: 80% !important;
    margin-right: auto !important;
    animation: slideInLeft 0.3s ease-out !important;
}

/* Input styling */
.input-container {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 25px !important;
    border: 2px solid transparent !important;
    background-clip: padding-box !important;
    padding: 15px 20px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}

.input-container:focus {
    background: rgba(255, 255, 255, 1) !important;
    border: 2px solid #667eea !important;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* Button styling */
.send-button {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
    border: none !important;
    border-radius: 50px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 30px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
}

.send-button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6) !important;
    background: linear-gradient(135deg, #FF8E53 0%, #FF6B6B 100%) !important;
}

.upload-button {
    background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%) !important;
    border: none !important;
    border-radius: 50px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 30px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(78, 205, 196, 0.4) !important;
}

.upload-button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(78, 205, 196, 0.6) !important;
}

/* Tabs styling */
.tab-nav {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 15px !important;
    padding: 5px !important;
    margin-bottom: 20px !important;
}

.tab-nav button {
    background: transparent !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.7) !important;
    padding: 12px 25px !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.tab-nav button.selected {
    background: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
}

/* Loading animations */
.typing-indicator {
    display: flex;
    align-items: center;
    padding: 15px 20px;
    background: rgba(78, 205, 196, 0.1);
    border-radius: 18px 18px 18px 5px;
    margin: 10px 0;
    max-width: 80px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4ECDC4;
    margin: 0 2px;
    animation: typingDots 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

/* Status indicators */
.status-online {
    color: #4ECDC4 !important;
    font-weight: 600 !important;
}

.status-offline {
    color: #FF6B6B !important;
    font-weight: 600 !important;
}

.feature-card {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 10px 0 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.feature-card:hover {
    background: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes rainbow {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(360deg); }
}

@keyframes typingDots {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
    }
}

/* Mobile responsive */
@media (max-width: 768px) {
    .main-container {
        margin: 10px !important;
        padding: 20px !important;
    }

    .header-text {
        font-size: 2rem !important;
    }

    .message.user, .message.bot {
        max-width: 90% !important;
    }
}

/* Fun interactive elements */
.emoji-reaction {
    font-size: 1.5rem;
    cursor: pointer;
    transition: transform 0.2s ease;
    margin: 0 5px;
}

.emoji-reaction:hover {
    transform: scale(1.3);
}

/* Progress bars */
.progress-bar {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    height: 6px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    background: linear-gradient(90deg, #4ECDC4, #44A08D);
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}
"""


class StudentChatbotUI:
    def __init__(self):
        self.api_base = API_BASE
        self.auth_token = None
        self.chat_history = []
        self.typing_animation = False

    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate user and store token"""
        try:
            response = requests.post(f"{self.api_base}/auth/login", json={
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                return True, "🎉 Welcome to the AI Study Buddy! Let's learn together!"
            else:
                return False, "❌ Invalid credentials. Try again!"

        except Exception as e:
            return False, f"🚫 Connection error: {str(e)}"

    def get_headers(self):
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    # Find this function in src/frontend/gradio_ui.py and replace it:

    def chat_with_ai(message: str,
                     history: List[List[str]],
                     use_context: bool = True) -> Tuple[List[List[str]],
                                                        str]:
        """Enhanced chat function with student-friendly responses"""
        if not self.auth_token:
            # For new format, append as dictionary
            history.append({"role": "user", "content": message})
            history.append(
                {"role": "assistant", "content": "🔐 Please log in first to start chatting!"})
            return history, ""

        if not message.strip():
            return history, ""

        # Add user message to history in new format
        history.append({"role": "user", "content": f"🧑‍🎓 {message}"})

        try:
            # Show typing indicator
            history.append({"role": "assistant", "content": "🤖 Thinking... 💭"})

            # Make API request (your existing API call code here)
            response = requests.post(f"{self.api_base}/chat",
                                     json={
                "message": message,
                "use_context": use_context,
                "max_context_docs": 3
            },
                headers=self.get_headers(),
                timeout=30
            )

            # Remove typing indicator
            history.pop()

            if response.status_code == 200:
                result = response.json()
                bot_response = result["bot_response"]

                # Add context info if available
                if result.get("context_documents"):
                    context_info = f"\n\n📚 *Used {
                        len(
                            result['context_documents'])} documents for context*"
                    bot_response += context_info

                # Add response time
                response_time = result.get("response_time_ms", 0)
                if response_time > 0:
                    bot_response += f"\n\n⚡ *Responded in {response_time}ms*"

                # Add bot response in new format
                history.append({"role": "assistant", "content": bot_response})

            else:
                history.append(
                    {"role": "assistant", "content": "🚨 Oops! Something went wrong. Please try again!"})

        except Exception as e:
            # Remove typing indicator if present
            if history and history[-1].get("content") == "🤖 Thinking... 💭":
                history.pop()

            error_msg = f"🚫 Connection error: {str(e)}"
            history.append({"role": "assistant", "content": error_msg})

        return history, ""

    def upload_document(self, file, filename: str = "") -> str:
        """Upload document with student-friendly feedback"""
        if not self.auth_token:
            return "🔐 Please log in first to upload documents!"

        if file is None:
            return "📁 Please select a file to upload!"

        try:
            # Read file content
            if hasattr(file, 'read'):
                content = file.read().decode('utf-8')
            else:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

            # Upload document
            response = requests.post(
                f"{
                    self.api_base}/documents",
                json={
                    "filename": filename or "uploaded_document.txt",
                    "content": content,
                    "metadata": {
                        "source": "student_upload",
                        "timestamp": time.time()}},
                headers=self.get_headers())

            if response.status_code == 200:
                result = response.json()
                analysis = result["analysis"]

                return f"""
🎉 **Document uploaded successfully!**

📊 **Analysis Results:**
- 📝 Words: {analysis['word_count']}
- 🔍 Keywords found: {len(analysis['keywords'])}
- 🏷️ Entities detected: {analysis['entities_found']}
- ⚡ Processed in: {result['processing_time_ms']}ms

🧠 **Top Keywords:** {', '.join(analysis['keywords'])}

✅ Your document is now available for AI chat context!
                """
            else:
                return "🚨 Upload failed. Please try again!"

        except Exception as e:
            return f"🚫 Upload error: {str(e)}"

    def semantic_search(self, query: str) -> str:
        """Perform semantic search with student-friendly results"""
        if not self.auth_token:
            return "🔐 Please log in first to search documents!"

        if not query.strip():
            return "🔍 Please enter a search query!"

        try:
            response = requests.post(f"{self.api_base}/search",
                                     json={
                "query": query,
                "limit": 5
            },
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()

                if result["total_results"] == 0:
                    return "🤷‍♀️ No documents found matching your search. Try different keywords!"

                search_results = f"""
🔍 **Search Results for:** "{query}"

🎯 **Found {result['total_results']} relevant documents:**

"""

                for i, doc in enumerate(result["results"], 1):
                    similarity_percentage = int(doc["similarity_score"] * 100)
                    search_results += f"""
**{i}. {doc['filename']}**
📊 Relevance: {similarity_percentage}%
📝 Preview: {doc['content_preview']}

---
"""

                search_results += f"\n⚡ Search completed in {
                    result['search_time_ms']}ms"
                return search_results

            else:
                return "🚨 Search failed. Please try again!"

        except Exception as e:
            return f"🚫 Search error: {str(e)}"


def create_student_ui():
    """Create the main student-friendly UI"""

    chatbot_ui = StudentChatbotUI()

    # Custom theme for students
    student_theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.teal,
        neutral_hue=gr.themes.colors.gray,
        font=[gr.themes.GoogleFont("Poppins"), "Arial", "sans-serif"]
    ).set(
        body_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        block_background_fill="rgba(255, 255, 255, 0.1)",
        block_border_width="1px",
        block_border_color="rgba(255, 255, 255, 0.2)",
        block_radius="15px",
        button_primary_background_fill="linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
        button_primary_background_fill_hover="linear-gradient(135deg, #FF8E53 0%, #FF6B6B 100%)"
    )

    with gr.Blocks(
        theme=student_theme,
        css=STUDENT_THEME_CSS,
        title="🤖 AI Study Buddy - Learn with AI!",
        analytics_enabled=False
    ) as demo:

        # Header
        gr.HTML("""
            <div class="main-container">
                <h1 class="header-text">🤖 AI Study Buddy</h1>
                <p class="subtitle-text">Your intelligent learning companion powered by advanced AI!</p>
            </div>
        """)

        # Authentication Section
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(
                    "<h3 style='color: white; text-align: center;'>🔐 Login to Get Started</h3>")
                username_input = gr.Textbox(
                    label="Username",
                    placeholder="Enter your username (try: admin)",
                    container=True
                )
                password_input = gr.Textbox(
                    label="Password",
                    placeholder="Enter password (try: secret)",
                    type="password",
                    container=True
                )
                login_btn = gr.Button(
                    "🚀 Login & Start Learning!",
                    variant="primary",
                    size="lg")
                login_status = gr.Textbox(
                    label="Status",
                    interactive=False,
                    placeholder="Please login to continue..."
                )

        # Main Interface Tabs
        with gr.Tabs() as tabs:

            # Chat Tab
            with gr.Tab("💬 AI Chat", id="chat"):
                gr.HTML(
                    "<h3 style='color: white; text-align: center;'>Chat with your AI study buddy!</h3>")

                with gr.Row():
                    with gr.Column(scale=4):
                        chatbot = gr.Chatbot(
                            height=500,
                            show_label=True,
                            container=True,
                            elem_classes=["chat-container"],
                            type="tuples"
                        )

                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder="Ask me anything! Try: 'Explain quantum physics simply' or 'Help me with math'",
                                container=False,
                                scale=4,
                                elem_classes=["input-container"])
                            send_btn = gr.Button(
                                "📤 Send", variant="primary", scale=1, elem_classes=["send-button"])

                        with gr.Row():
                            clear_btn = gr.Button(
                                "🗑️ Clear Chat", variant="secondary")
                            context_toggle = gr.Checkbox(
                                label="📚 Use uploaded documents for context",
                                value=True,
                                info="Enable this to make the AI use your uploaded documents for better answers!"
                            )

                    with gr.Column(scale=1):
                        gr.HTML("<h4 style='color: white;'>💡 Quick Tips</h4>")
                        gr.HTML("""
                            <div class="feature-card">
                                <h5>🎯 Ask Specific Questions</h5>
                                <p>Be specific! Instead of "help with math", try "explain quadratic equations with examples"</p>
                            </div>
                            <div class="feature-card">
                                <h5>📚 Upload Study Materials</h5>
                                <p>Upload your notes, textbooks, or articles to get personalized help!</p>
                            </div>
                            <div class="feature-card">
                                <h5>🔍 Use Semantic Search</h5>
                                <p>Search through your uploaded documents to find relevant information quickly!</p>
                            </div>
                        """)

            # Document Upload Tab
            with gr.Tab("📁 Upload Study Materials", id="upload"):
                gr.HTML(
                    "<h3 style='color: white; text-align: center;'>Upload your study materials for smarter AI responses!</h3>")

                with gr.Row():
                    with gr.Column():
                        file_upload = gr.File(
                            label="📄 Choose your study material",
                            file_types=[".txt", ".md", ".py", ".json"],
                            type="filepath"
                        )
                        filename_input = gr.Textbox(
                            label="📝 Give your document a name",
                            placeholder="e.g., 'Biology Chapter 5' or 'Python Notes'")
                        upload_btn = gr.Button(
                            "📤 Upload Document",
                            variant="primary",
                            size="lg",
                            elem_classes=["upload-button"])
                        upload_result = gr.Textbox(
                            label="Upload Status",
                            interactive=False,
                            lines=10
                        )

            # Search Tab
            with gr.Tab("🔍 Smart Search", id="search"):
                gr.HTML(
                    "<h3 style='color: white; text-align: center;'>Search through your uploaded documents with AI!</h3>")

                with gr.Row():
                    with gr.Column():
                        search_input = gr.Textbox(
                            label="🔍 What are you looking for?",
                            placeholder="e.g., 'photosynthesis process' or 'python loops examples'",
                            lines=2)
                        search_btn = gr.Button(
                            "🔍 Smart Search", variant="primary", size="lg")
                        search_results = gr.Textbox(
                            label="Search Results",
                            interactive=False,
                            lines=15
                        )

            # Help Tab
            with gr.Tab("❓ How to Use", id="help"):
                gr.HTML("""
                    <div style="color: white; padding: 20px;">
                        <h3 style="text-align: center;">🌟 How to Make the Most of Your AI Study Buddy</h3>

                        <div class="feature-card">
                            <h4>🚀 Getting Started</h4>
                            <ol>
                                <li>Login with your credentials (username: admin, password: secret for demo)</li>
                                <li>Upload your study materials in the "Upload" tab</li>
                                <li>Start chatting with your AI study buddy!</li>
                            </ol>
                        </div>

                        <div class="feature-card">
                            <h4>💬 Chat Features</h4>
                            <ul>
                                <li><strong>Context-Aware:</strong> The AI uses your uploaded documents to give better answers</li>
                                <li><strong>Real-time:</strong> Get instant responses to your questions</li>
                                <li><strong>Smart:</strong> Understands complex topics and explains them simply</li>
                            </ul>
                        </div>

                        <div class="feature-card">
                            <h4>🔍 Search Features</h4>
                            <ul>
                                <li><strong>Semantic Search:</strong> Finds relevant information even if keywords don't match exactly</li>
                                <li><strong>Relevance Scoring:</strong> Shows how relevant each result is to your query</li>
                                <li><strong>Quick Preview:</strong> See document previews before diving deeper</li>
                            </ul>
                        </div>

                        <div class="feature-card">
                            <h4>🎯 Pro Tips</h4>
                            <ul>
                                <li>Upload lecture notes, textbooks, and articles for personalized help</li>
                                <li>Ask follow-up questions to dive deeper into topics</li>
                                <li>Use specific examples in your questions for better answers</li>
                                <li>Try different search terms if you don't find what you're looking for</li>
                            </ul>
                        </div>

                        <div class="feature-card">
                            <h4>🤖 What Makes This Special?</h4>
                            <ul>
                                <li><strong>Quantized LLM:</strong> Runs efficiently on any hardware</li>
                                <li><strong>NLP Processing:</strong> Understands context and meaning</li>
                                <li><strong>Semantic Search:</strong> Finds information by meaning, not just keywords</li>
                                <li><strong>Privacy-First:</strong> Your data stays secure and private</li>
                            </ul>
                        </div>
                    </div>
                """)

        # Event handlers
        def handle_login(username, password):
            success, message = chatbot_ui.authenticate(username, password)
            return message

        def handle_chat(message, history, use_context):
            return chatbot_ui.chat_with_ai(message, use_context)

        def handle_upload(file, filename):
            return chatbot_ui.upload_document(file, filename)

        def handle_search(query):
            return chatbot_ui.semantic_search(query)

        def clear_chat():
            return []

        # Connect event handlers
        login_btn.click(
            handle_login,
            inputs=[username_input, password_input],
            outputs=[login_status]
        )

        # Chat functionality
        msg_input.submit(
            handle_chat,
            inputs=[msg_input, chatbot, context_toggle],
            outputs=[chatbot, msg_input]
        )

        send_btn.click(
            handle_chat,
            inputs=[msg_input, chatbot, context_toggle],
            outputs=[chatbot, msg_input]
        )

        clear_btn.click(clear_chat, outputs=[chatbot])

        # Upload functionality
        upload_btn.click(
            handle_upload,
            inputs=[file_upload, filename_input],
            outputs=[upload_result]
        )

        # Search functionality
        search_btn.click(
            handle_search,
            inputs=[search_input],
            outputs=[search_results]
        )

        search_input.submit(
            handle_search,
            inputs=[search_input],
            outputs=[search_results]
        )

    return demo


# Launch the interface
if __name__ == "__main__":
    demo = create_student_ui()

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        # show_tips=True,  # Remove this line
        # enable_queue=True,  # Remove this line - deprecated
        # max_threads=10  # Remove this line - deprecated
    )
