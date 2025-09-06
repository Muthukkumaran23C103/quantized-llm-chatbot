#!/usr/bin/env python3
"""
Student-Friendly Quantized LLM Chatbot with Enhanced Voice & Document Upload
Modern animated UI designed specifically for students
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
UPLOAD_DIR = Path("./uploaded_documents")
UPLOAD_DIR.mkdir(exist_ok=True)

# Student-friendly configuration
STUDENT_LANGUAGES = {
    "en": {"name": "English 🇺🇸", "flag": "🇺🇸", "greeting": "Hello! Ready to learn?"},
    "ta": {"name": "Tamil 🇮🇳", "flag": "🇮🇳", "greeting": "வணக்கம்! படிக்க தயாரா?"},
    "hi": {"name": "Hindi 🇮🇳", "flag": "🇮🇳", "greeting": "नमस्ते! पढ़ने के लिए तैयार हैं?"},
    "es": {"name": "Spanish 🇪🇸", "flag": "🇪🇸", "greeting": "¡Hola! ¿Listo para aprender?"},
    "fr": {"name": "French 🇫🇷", "flag": "🇫🇷", "greeting": "Salut! Prêt à apprendre?"},
    "de": {"name": "German 🇩🇪", "flag": "🇩🇪", "greeting": "Hallo! Bereit zum Lernen?"}
}

# Global state for students
class StudentChatbotState:
    def __init__(self):
        self.auth_token = None
        self.student_name = None
        self.conversation_history = []
        self.current_language = "en"
        self.voice_enabled = True
        self.uploaded_documents = []
        self.study_session_start = None
        self.questions_asked = 0
        self.learning_topics = set()

state = StudentChatbotState()

def process_document_upload(files) -> str:
    """Process uploaded documents with animations and feedback"""
    if not files:
        return create_upload_status("❌ No files selected", "error")
    
    if not state.auth_token:
        return create_upload_status("🔐 Please log in first to upload documents", "warning")
    
    try:
        processed_files = []
        total_files = len(files) if isinstance(files, list) else 1
        files_list = files if isinstance(files, list) else [files]
        
        for i, file in enumerate(files_list):
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
                    
                    # Save to upload directory
                    file_hash = hashlib.md5(text_content.encode()).hexdigest()[:8]
                    safe_filename = f"{file_hash}_{filename}"
                    file_path = UPLOAD_DIR / safe_filename
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    
                    # Add to state
                    doc_info = {
                        "filename": filename,
                        "path": str(file_path),
                        "size": len(text_content),
                        "uploaded_at": datetime.now().isoformat(),
                        "word_count": len(text_content.split()),
                        "topics": extract_topics(text_content[:500])
                    }
                    
                    state.uploaded_documents.append(doc_info)
                    processed_files.append(doc_info)
                    
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    continue
        
        if processed_files:
            return create_upload_success(processed_files)
        else:
            return create_upload_status("❌ Failed to process any files", "error")
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return create_upload_status(f"❌ Upload failed: {str(e)}", "error")

def extract_topics(text: str) -> List[str]:
    """Extract potential study topics from text"""
    import re
    
    # Simple topic extraction based on common academic keywords
    academic_keywords = {
        'mathematics': ['math', 'algebra', 'geometry', 'calculus', 'statistics'],
        'science': ['physics', 'chemistry', 'biology', 'molecule', 'atom', 'cell'],
        'history': ['history', 'war', 'empire', 'civilization', 'ancient', 'medieval'],
        'literature': ['literature', 'poem', 'novel', 'author', 'character', 'theme'],
        'computer_science': ['programming', 'algorithm', 'code', 'software', 'computer'],
        'language': ['language', 'grammar', 'vocabulary', 'pronunciation', 'translation']
    }
    
    text_lower = text.lower()
    found_topics = []
    
    for topic, keywords in academic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            found_topics.append(topic.replace('_', ' ').title())
    
    return found_topics[:3]  # Return up to 3 topics

def create_upload_success(files: List[Dict]) -> str:
    """Create animated success message for uploads"""
    total_words = sum(f['word_count'] for f in files)
    topics = set()
    for f in files:
        topics.update(f['topics'])
    
    files_html = ""
    for i, file in enumerate(files):
        topics_str = ", ".join(file['topics']) if file['topics'] else "General Study Material"
        files_html += f"""
        <div class="uploaded-file animate-slide-up" style="animation-delay: {i * 0.1}s;">
            <div class="file-info">
                <div class="file-name">📄 {file['filename']}</div>
                <div class="file-details">
                    📊 {file['word_count']} words • 🏷️ {topics_str}
                </div>
            </div>
            <div class="file-status">✅</div>
        </div>
        """
    
    return f"""
    <div class="upload-success animate-bounce-in">
        <div class="success-header">
            <div class="success-icon animate-pulse">🎉</div>
            <div class="success-title">Documents Successfully Uploaded!</div>
        </div>
        
        <div class="upload-stats">
            <div class="stat-item animate-fade-in" style="animation-delay: 0.2s;">
                <div class="stat-number">{len(files)}</div>
                <div class="stat-label">Files Processed</div>
            </div>
            <div class="stat-item animate-fade-in" style="animation-delay: 0.4s;">
                <div class="stat-number">{total_words:,}</div>
                <div class="stat-label">Total Words</div>
            </div>
            <div class="stat-item animate-fade-in" style="animation-delay: 0.6s;">
                <div class="stat-number">{len(topics)}</div>
                <div class="stat-label">Study Topics</div>
            </div>
        </div>
        
        <div class="uploaded-files">
            {files_html}
        </div>
        
        <div class="upload-actions animate-slide-up" style="animation-delay: 0.8s;">
            <div class="action-tip">
                💡 <strong>Pro Tip:</strong> Ask me questions about your uploaded documents!
            </div>
        </div>
    </div>
    """

def create_upload_status(message: str, status_type: str) -> str:
    """Create status message with appropriate styling"""
    status_config = {
        "success": {"icon": "✅", "color": "#4CAF50"},
        "error": {"icon": "❌", "color": "#f44336"},
        "warning": {"icon": "⚠️", "color": "#ff9800"},
        "info": {"icon": "ℹ️", "color": "#2196F3"}
    }
    
    config = status_config.get(status_type, status_config["info"])
    
    return f"""
    <div class="upload-status {status_type} animate-shake">
        <div class="status-icon">{config['icon']}</div>
        <div class="status-message">{message}</div>
    </div>
    """

def login_student(username: str, password: str) -> str:
    """Student-friendly login with welcome animation"""
    if not username or not password:
        return create_login_status("Please enter your name and a password to start learning! 📚", "warning")
    
    # Accept any login for demo
    state.auth_token = f"student_{username}_{int(time.time())}"
    state.student_name = username
    state.study_session_start = datetime.now()
    
    greeting = STUDENT_LANGUAGES[state.current_language]["greeting"]
    
    return f"""
    <div class="login-success animate-bounce-in">
        <div class="welcome-animation">
            <div class="welcome-emoji animate-bounce">🎓</div>
            <div class="welcome-text">
                <h3>Welcome to Your AI Study Buddy!</h3>
                <p class="student-greeting">{greeting}</p>
            </div>
        </div>
        
        <div class="student-dashboard">
            <div class="dashboard-item animate-slide-up" style="animation-delay: 0.2s;">
                <div class="dashboard-icon">🤖</div>
                <div class="dashboard-content">
                    <div class="dashboard-title">AI Tutor Ready</div>
                    <div class="dashboard-desc">Ask me anything!</div>
                </div>
            </div>
            
            <div class="dashboard-item animate-slide-up" style="animation-delay: 0.4s;">
                <div class="dashboard-icon">🎤</div>
                <div class="dashboard-content">
                    <div class="dashboard-title">Voice Learning</div>
                    <div class="dashboard-desc">Speak in 6 languages</div>
                </div>
            </div>
            
            <div class="dashboard-item animate-slide-up" style="animation-delay: 0.6s;">
                <div class="dashboard-icon">📚</div>
                <div class="dashboard-content">
                    <div class="dashboard-title">Smart Documents</div>
                    <div class="dashboard-desc">Upload & analyze</div>
                </div>
            </div>
        </div>
        
        <div class="study-motivation animate-fade-in" style="animation-delay: 0.8s;">
            <div class="motivation-text">
                "Every expert was once a beginner. Every pro was once an amateur." 💫
            </div>
        </div>
    </div>
    """

def create_login_status(message: str, status_type: str) -> str:
    """Create animated login status"""
    return f"""
    <div class="login-status {status_type} animate-pulse">
        <div class="status-content">
            {message}
        </div>
    </div>
    """

def student_chat_with_ai(message: str, history: List) -> Tuple[List, str, str]:
    """Student-focused AI chat with educational responses"""
    if not state.auth_token:
        if history is None:
            history = []
        history.append([message, "🔐 Hi there! Please log in first to start your learning journey! 📚"])
        return history, "", ""
    
    if not message.strip():
        return history, "", ""
    
    if history is None:
        history = []
    
    # Update student stats
    state.questions_asked += 1
    
    try:
        message_lower = message.lower()
        
        # Detect study topics and add to learning topics
        topics = extract_topics(message)
        state.learning_topics.update(topics)
        
        # Student-focused AI responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            ai_response = f"""🎓 **Hey {state.student_name}! Ready to learn something awesome?**

I'm your AI study buddy, here to make learning fun and effective! Here's what I can do for you:

📚 **Study Help**
- Answer questions on any subject
- Explain complex concepts simply
- Help with homework and projects

🎤 **Voice Learning** 
- Practice pronunciation in 6 languages
- Listen to explanations while you study
- Hands-free learning experience

📄 **Smart Study Materials**
- Upload your notes, textbooks, PDFs
- Ask questions about your documents
- Get instant summaries and explanations

💡 **Study Tips**
- Personalized learning strategies  
- Memory techniques and mnemonics
- Exam preparation guidance

What would you like to explore first? 🚀"""

        elif any(word in message_lower for word in ['help', 'stuck', 'confused', 'difficult']):
            ai_response = f"""🤗 **Don't worry {state.student_name}, I'm here to help!**

When you're stuck, try these strategies:

🧩 **Break It Down**
- Split complex problems into smaller parts
- Focus on one concept at a time
- Connect new info to what you already know

🔍 **Active Learning**
- Ask yourself "why" and "how" questions
- Teach the concept to an imaginary student
- Create mind maps or diagrams

🎯 **Practice Techniques**
- Use the Feynman Technique (explain in simple terms)
- Try spaced repetition for memorization
- Practice with real examples

💪 **Stay Motivated**
- Celebrate small wins
- Take breaks when needed
- Remember: struggling means you're learning!

What specific topic are you finding challenging? Let's tackle it together! 💫"""

        elif any(word in message_lower for word in ['exam', 'test', 'quiz', 'preparation']):
            ai_response = """📝 **Exam Prep Mode Activated! Let's ace this! 🎯**

**Smart Study Strategy:**

🗓️ **Planning Phase**
- Create a study timeline
- Identify key topics and weak areas
- Set daily study goals

📖 **Active Study Methods**
- Summarize each topic in your own words
- Create flashcards for key concepts
- Practice past papers and sample questions

🧠 **Memory Boosters**
- Use mnemonics for lists and formulas
- Create visual associations
- Study in different locations

⚡ **Last-Minute Tips**
- Review your notes, don't cram new material
- Get good sleep before the exam
- Stay hydrated and eat brain food

🎤 **Use Voice Learning:**
- Record yourself explaining concepts
- Listen to summaries while walking
- Practice presentations out loud

What subject is your exam on? I can create a personalized study plan! 📊"""

        elif any(word in message_lower for word in ['motivation', 'tired', 'boring', 'give up']):
            ai_response = f"""💪 **Hey {state.student_name}, I believe in you! You've got this! 🌟**

**Motivation Boost Incoming:**

🎯 **Remember Your Why**
- Think about your goals and dreams
- Visualize your future success
- Every small step counts!

🎮 **Make It Fun**
- Gamify your learning (set levels/rewards)
- Study with friends or form study groups
- Use colorful notes and visual aids

⚡ **Energy Boosters**
- Take 5-minute breaks every 25 minutes
- Do light exercise or stretching
- Change your study environment

🏆 **Celebrate Progress**
- Acknowledge what you've already learned
- Reward yourself for milestones
- Track your improvement over time

🤖 **I'm Here for You**
- Ask me to explain things differently
- Use voice mode for variety
- Upload your materials for personalized help

Remember: "You are braver than you believe, stronger than you seem, and smarter than you think!" ✨

What's one small thing we can tackle right now? 🚀"""

        elif any(word in message_lower for word in ['document', 'uploaded', 'file', 'notes']):
            if state.uploaded_documents:
                doc_list = "\n".join([f"📄 {doc['filename']} ({doc['word_count']} words)" 
                                    for doc in state.uploaded_documents[-3:]])
                ai_response = f"""📚 **Your Study Documents Are Ready!**

**Recently Uploaded:**
{doc_list}

**What You Can Do:**
🔍 **Ask Specific Questions**
- "Explain the main points in chapter 3"
- "What are the key formulas in my math notes?"
- "Summarize the historical timeline"

🎯 **Get Targeted Help**
- "Create flashcards from this document"
- "What should I focus on for the exam?"
- "Find examples of [specific concept]"

💡 **Study Techniques**
- "Quiz me on this material"
- "Explain [concept] in simple terms"
- "Connect this to real-world examples"

Just ask me anything about your uploaded materials! I've analyzed them and I'm ready to help you master the content! 🚀"""
            else:
                ai_response = """📄 **Ready to Upload Your Study Materials!**

**Supported Files:**
- 📝 Text files (.txt, .md)
- 📄 PDF documents
- 📋 Word documents (.docx)
- 📚 Study notes and textbooks

**What Happens After Upload:**
✅ I analyze the content instantly
✅ Extract key topics and concepts  
✅ Prepare personalized Q&A
✅ Create study summaries

**Pro Tips:**
💡 Upload your textbook chapters
💡 Add your class notes
💡 Include homework assignments
💡 Upload practice problems

Drag and drop your files in the upload area, and let's supercharge your learning! 🚀"""

        else:
            # Generate contextual response based on uploaded documents
            context_info = ""
            if state.uploaded_documents:
                recent_topics = set()
                for doc in state.uploaded_documents[-2:]:
                    recent_topics.update(doc['topics'])
                if recent_topics:
                    context_info = f"\n\n📚 **Related to your uploaded materials:** {', '.join(list(recent_topics)[:3])}"
            
            ai_response = f"""🤖 **Great question about "{message}"!**

Let me help you understand this concept step by step:

🎯 **Key Points to Remember:**
- This topic connects to fundamental principles in your field of study
- Understanding the "why" is just as important as the "what"
- Practice with examples helps cement the knowledge

💡 **Learning Strategy:**
- Break down complex ideas into smaller components
- Connect new information to what you already know
- Ask follow-up questions to deepen understanding

🗣️ **Try Voice Mode:**
- Click the microphone to ask follow-up questions
- I can explain concepts in different languages
- Hear explanations while you take notes

📊 **Your Learning Progress:**
- Questions asked today: {state.questions_asked}
- Study topics explored: {len(state.learning_topics)}
- Documents uploaded: {len(state.uploaded_documents)}{context_info}

What specific aspect would you like me to explain further? I'm here to help you master this! 🚀"""

        # Add to conversation history
        history.append([message, ai_response])
        
        # Clean text for TTS (student-friendly)
        tts_text = clean_student_tts(ai_response)
        
        return history, "", tts_text
        
    except Exception as e:
        error_msg = f"🤗 Oops! I encountered a small hiccup: {str(e)}. Let's try that again!"
        history.append([message, error_msg])
        return history, "", "Sorry, let me try to help you in a different way."

def clean_student_tts(text: str) -> str:
    """Clean text for student-friendly TTS"""
    import re
    
    # Remove emojis and markdown
    text = re.sub(r'[🤖🎓🚀📊🧠❌🚫⚡🔥💡🎤🔊📚🌍🐳💾📄🔍🎯💪🤗✨🌟💫🏆🎮⚡🎯📝🗓️📖🧠💡🔍🎯]', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    
    # Make more conversational for students
    text = text.replace('AI', 'A I')
    text = text.replace('Let me help you understand', 'Let me help you')
    text = text.replace('Here\'s what', 'Here is what')
    
    # Clean up and limit length for TTS
    sentences = text.split('.')
    clean_sentences = []
    for sentence in sentences[:4]:  # Limit to first 4 sentences for TTS
        sentence = sentence.strip()
        if sentence and len(sentence) > 10:
            clean_sentences.append(sentence)
    
    return '. '.join(clean_sentences) + '.'

def search_student_documents(query: str) -> str:
    """Student-friendly document search"""
    if not state.auth_token:
        return create_search_status("🔐 Please log in first to search your documents!", "warning")
    
    if not query.strip():
        return create_search_status("📝 Type something to search for in your documents!", "info")
    
    if not state.uploaded_documents:
        return create_search_status("📚 Upload some documents first, then search away!", "info")
    
    # Simulate search (in real implementation, this would use actual search)
    try:
        # Simple text search simulation
        search_results = []
        query_lower = query.lower()
        
        for doc in state.uploaded_documents:
            # Read document content
            try:
                with open(doc['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query_lower in content.lower():
                    # Find context around the match
                    lines = content.split('\n')
                    matching_lines = []
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            start = max(0, i-1)
                            end = min(len(lines), i+2)
                            context = ' '.join(lines[start:end]).strip()
                            matching_lines.append(context[:200] + "..." if len(context) > 200 else context)
                            if len(matching_lines) >= 2:
                                break
                    
                    if matching_lines:
                        search_results.append({
                            'filename': doc['filename'],
                            'matches': matching_lines,
                            'relevance': 85 + len(matching_lines) * 5
                        })
            except Exception as e:
                logger.error(f"Error searching {doc['filename']}: {e}")
                continue
        
        if search_results:
            return create_search_results(query, search_results)
        else:
            return create_search_status(f"🔍 No matches found for '{query}'. Try different keywords!", "info")
            
    except Exception as e:
        return create_search_status(f"❌ Search error: {str(e)}", "error")

def create_search_results(query: str, results: List[Dict]) -> str:
    """Create animated search results"""
    results_html = ""
    for i, result in enumerate(results):
        matches_html = ""
        for j, match in enumerate(result['matches']):
            matches_html += f"""
            <div class="search-match animate-fade-in" style="animation-delay: {(i * 0.2) + (j * 0.1)}s;">
                📝 {match}
            </div>
            """
        
        results_html += f"""
        <div class="search-result animate-slide-up" style="animation-delay: {i * 0.2}s;">
            <div class="result-header">
                <div class="result-title">📄 {result['filename']}</div>
                <div class="result-relevance">{result['relevance']}% match</div>
            </div>
            <div class="result-matches">
                {matches_html}
            </div>
        </div>
        """
    
    return f"""
    <div class="search-results animate-bounce-in">
        <div class="search-header">
            <div class="search-icon animate-pulse">🔍</div>
            <div class="search-title">Found {len(results)} results for "{query}"</div>
        </div>
        
        <div class="results-container">
            {results_html}
        </div>
        
        <div class="search-tips animate-fade-in" style="animation-delay: 0.8s;">
            <div class="tip-title">💡 Search Tips:</div>
            <div class="tips-list">
                • Try keywords from your study materials<br>
                • Search for formulas, definitions, or concepts<br>
                • Use quotes for exact phrases: "photosynthesis process"
            </div>
        </div>
    </div>
    """

def create_search_status(message: str, status_type: str) -> str:
    """Create animated search status"""
    return f"""
    <div class="search-status {status_type} animate-bounce">
        <div class="status-content">
            {message}
        </div>
    </div>
    """

def clear_student_chat():
    """Clear chat with encouraging message"""
    return [], ""

def create_student_interface():
    """Create the ultimate student-friendly interface with animations"""
    
    # Enhanced student-friendly CSS with lots of animations
    student_css = """
    /* Student-Friendly Animated CSS */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    :root {
        --student-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --student-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --student-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --student-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --student-warning: linear-gradient(135deg, #fcb045 0%, #fd1d1d 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
    }
    
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .gradio-container {
        background: var(--student-primary) !important;
        color: white !important;
        min-height: 100vh !important;
    }
    
    /* Animations */
    @keyframes bounce-in {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.1); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes slide-up {
        0% { transform: translateY(30px); opacity: 0; }
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
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(79, 172, 254, 0.3); }
        50% { box-shadow: 0 0 30px rgba(79, 172, 254, 0.7); }
    }
    
    /* Apply animations */
    .animate-bounce-in { animation: bounce-in 0.6s ease-out; }
    .animate-slide-up { animation: slide-up 0.5s ease-out; }
    .animate-fade-in { animation: fade-in 0.4s ease-out; }
    .animate-pulse { animation: pulse 2s infinite; }
    .animate-shake { animation: shake 0.5s ease-out; }
    .animate-float { animation: float 3s ease-in-out infinite; }
    .animate-glow { animation: glow 2s ease-in-out infinite; }
    
    /* Student-friendly cards */
    .student-card {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin: 15px 0 !important;
        border: 2px solid var(--glass-border) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .student-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Voice button - enhanced for students */
    .student-voice-btn {
        background: var(--student-accent) !important;
        border: 4px solid white !important;
        border-radius: 50% !important;
        width: 140px !important;
        height: 140px !important;
        font-size: 4rem !important;
        color: white !important;
        cursor: pointer !important;
        margin: 20px auto !important;
        display: block !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .student-voice-btn:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 20px 50px rgba(79, 172, 254, 0.5) !important;
    }
    
    .student-voice-btn.listening {
        background: var(--student-success) !important;
        animation: glow 1s infinite !important;
    }
    
    .student-voice-btn.listening::before {
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        left: -50% !important;
        width: 200% !important;
        height: 200% !important;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent) !important;
        transform: rotate(45deg) !important;
        animation: shine 2s infinite !important;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    /* Upload area - student friendly */
    .upload-area {
        background: var(--glass-bg) !important;
        border: 3px dashed var(--glass-border) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .upload-area:hover {
        border-color: #4facfe !important;
        background: rgba(79, 172, 254, 0.1) !important;
        transform: scale(1.02) !important;
    }
    
    .upload-area.dragover {
        border-color: #00f2fe !important;
        background: rgba(0, 242, 254, 0.2) !important;
        transform: scale(1.05) !important;
    }
    
    /* Chat bubbles - enhanced for students */
    .student-message {
        background: var(--student-accent) !important;
        color: white !important;
        border-radius: 20px 20px 5px 20px !important;
        padding: 15px 20px !important;
        margin: 10px !important;
        max-width: 80% !important;
        margin-left: auto !important;
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3) !important;
    }
    
    .ai-message {
        background: var(--glass-bg) !important;
        border: 2px solid var(--glass-border) !important;
        border-radius: 20px 20px 20px 5px !important;
        padding: 15px 20px !important;
        margin: 10px !important;
        max-width: 80% !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Upload success animation */
    .upload-success {
        background: var(--glass-bg) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        border: 2px solid rgba(76, 175, 80, 0.5) !important;
        text-align: center !important;
    }
    
    .success-header {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 20px !important;
        gap: 15px !important;
    }
    
    .success-icon {
        font-size: 3rem !important;
    }
    
    .success-title {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #4CAF50 !important;
    }
    
    .upload-stats {
        display: flex !important;
        justify-content: space-around !important;
        margin: 30px 0 !important;
        flex-wrap: wrap !important;
    }
    
    .stat-item {
        text-align: center !important;
        padding: 15px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        min-width: 100px !important;
        margin: 5px !important;
    }
    
    .stat-number {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #4facfe !important;
    }
    
    .stat-label {
        font-size: 0.9rem !important;
        opacity: 0.8 !important;
        margin-top: 5px !important;
    }
    
    .uploaded-files {
        margin: 20px 0 !important;
    }
    
    .uploaded-file {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        backdrop-filter: blur(5px) !important;
    }
    
    .file-info {
        flex: 1 !important;
    }
    
    .file-name {
        font-weight: 600 !important;
        margin-bottom: 5px !important;
    }
    
    .file-details {
        font-size: 0.85rem !important;
        opacity: 0.7 !important;
    }
    
    .file-status {
        font-size: 1.5rem !important;
        margin-left: 15px !important;
    }
    
    /* Login success */
    .login-success {
        background: var(--glass-bg) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        text-align: center !important;
        border: 2px solid rgba(76, 175, 80, 0.5) !important;
    }
    
    .welcome-animation {
        margin-bottom: 30px !important;
    }
    
    .welcome-emoji {
        font-size: 4rem !important;
        margin-bottom: 15px !important;
    }
    
    .welcome-text h3 {
        color: #4CAF50 !important;
        font-size: 1.8rem !important;
        margin-bottom: 10px !important;
    }
    
    .student-greeting {
        font-size: 1.2rem !important;
        opacity: 0.9 !important;
    }
    
    .student-dashboard {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
        gap: 15px !important;
        margin: 20px 0 !important;
    }
    
    .dashboard-item {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        text-align: center !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .dashboard-item:hover {
        transform: translateY(-5px) !important;
        background: rgba(255, 255, 255, 0.2) !important;
    }
    
    .dashboard-icon {
        font-size: 2.5rem !important;
        margin-bottom: 10px !important;
    }
    
    .dashboard-title {
        font-weight: 600 !important;
        margin-bottom: 5px !important;
    }
    
    .dashboard-desc {
        font-size: 0.9rem !important;
        opacity: 0.8 !important;
    }
    
    .study-motivation {
        background: var(--student-accent) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-top: 20px !important;
        text-align: center !important;
    }
    
    .motivation-text {
        font-style: italic !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* Responsive design for students */
    @media (max-width: 768px) {
        .student-card {
            margin: 10px 5px !important;
            padding: 20px !important;
        }
        
        .student-voice-btn {
            width: 120px !important;
            height: 120px !important;
            font-size: 3rem !important;
        }
        
        .upload-stats {
            flex-direction: column !important;
        }
        
        .student-dashboard {
            grid-template-columns: 1fr !important;
        }
    }
    
    /* Status messages */
    .upload-status, .search-status, .login-status {
        background: var(--glass-bg) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin: 15px 0 !important;
        text-align: center !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid var(--glass-border) !important;
    }
    
    .upload-status.success, .search-status.success, .login-status.success {
        border-color: rgba(76, 175, 80, 0.7) !important;
    }
    
    .upload-status.error, .search-status.error, .login-status.error {
        border-color: rgba(244, 67, 54, 0.7) !important;
    }
    
    .upload-status.warning, .search-status.warning, .login-status.warning {
        border-color: rgba(255, 152, 0, 0.7) !important;
    }
    
    /* Search results */
    .search-results {
        background: var(--glass-bg) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid var(--glass-border) !important;
    }
    
    .search-header {
        display: flex !important;
        align-items: center !important;
        margin-bottom: 20px !important;
        gap: 15px !important;
    }
    
    .search-icon {
        font-size: 2rem !important;
    }
    
    .search-title {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }
    
    .search-result {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin: 15px 0 !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .result-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 15px !important;
    }
    
    .result-title {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    .result-relevance {
        background: var(--student-accent) !important;
        color: white !important;
        padding: 5px 10px !important;
        border-radius: 15px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    
    .search-match {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        margin: 8px 0 !important;
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
    }
    
    .search-tips {
        background: var(--student-accent) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-top: 20px !important;
    }
    
    .tip-title {
        font-weight: 600 !important;
        margin-bottom: 8px !important;
    }
    
    .tips-list {
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
    }
    """
    
    # Enhanced JavaScript with better STT/TTS
    student_voice_js = """
    <script>
    console.log('🎓 Initializing Student Voice Learning System...');
    
    // Enhanced voice system for students
    let recognition = null;
    let synthesis = window.speechSynthesis;
    let isListening = false;
    let isProcessing = false;
    let currentLanguage = 'en';
    let voices = [];
    let lastTTSText = '';
    let voiceVisualization = null;
    
    // Student-friendly language configuration
    const studentLanguages = {
        'en': { 
            code: 'en-US', 
            name: 'English', 
            flag: '🇺🇸',
            encouragement: 'Great job speaking in English!'
        },
        'ta': { 
            code: 'ta-IN', 
            name: 'Tamil', 
            flag: '🇮🇳',
            encouragement: 'நன்றாக தமிழில் பேசினீர்கள்!'
        },
        'hi': { 
            code: 'hi-IN', 
            name: 'Hindi', 
            flag: '🇮🇳',
            encouragement: 'हिंदी में बहुत अच्छा बोले!'
        },
        'es': { 
            code: 'es-ES', 
            name: 'Spanish', 
            flag: '🇪🇸',
            encouragement: '¡Excelente español!'
        },
        'fr': { 
            code: 'fr-FR', 
            name: 'French', 
            flag: '🇫🇷',
            encouragement: 'Excellent français!'
        },
        'de': { 
            code: 'de-DE', 
            name: 'German', 
            flag: '🇩🇪',
            encouragement: 'Ausgezeichnetes Deutsch!'
        }
    };
    
    // Initialize enhanced voice system
    function initStudentVoiceSystem() {
        console.log('🚀 Setting up enhanced voice learning...');
        
        // Load available voices
        synthesis.addEventListener('voiceschanged', loadVoices);
        loadVoices();
        
        // Setup enhanced speech recognition
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            setupSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            recognition = new SpeechRecognition();
            setupSpeechRecognition();
        } else {
            console.warn('⚠️ Speech recognition not supported');
            showVoiceStatus('❌ Voice not supported - Please use Chrome or Edge', 'error');
            return false;
        }
        
        // Setup audio visualization
        setupAudioVisualization();
        
        console.log('✅ Student voice system ready!');
        showVoiceStatus('🎤 Ready to learn! Click the microphone to start', 'ready');
        return true;
    }
    
    function loadVoices() {
        voices = synthesis.getVoices();
        console.log(`🎙️ Loaded ${voices.length} voices`);
        
        // Debug: List available voices
        voices.forEach((voice, index) => {
            console.log(`Voice ${index}: ${voice.name} (${voice.lang})`);
        });
    }
    
    function setupSpeechRecognition() {
        // Enhanced settings for students
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 3;
        recognition.lang = studentLanguages[currentLanguage].code;
        
        // Event handlers with student-friendly feedback
        recognition.onstart = function() {
            console.log('🎤 Student voice recognition started');
            isListening = true;
            updateVoiceButton('listening');
            showVoiceStatus('🎤 Listening... Speak clearly!', 'listening');
            playEncouraementSound();
        };
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Show interim results for better UX
            if (interimTranscript) {
                showVoiceStatus(`🎤 Hearing: "${interimTranscript}..."`, 'processing');
            }
            
            if (finalTranscript) {
                console.log('✅ Final transcript:', finalTranscript);
                const confidence = event.results[event.results.length - 1][0].confidence || 0.8;
                
                fillMessageInput(finalTranscript);
                showVoiceStatus(`✅ Got it! "${finalTranscript}" (${Math.round(confidence * 100)}% confident)`, 'success');
                
                // Encourage the student
                if (confidence > 0.7) {
                    setTimeout(() => {
                        const encouragement = studentLanguages[currentLanguage].encouragement;
                        showVoiceStatus(`🌟 ${encouragement}`, 'success');
                    }, 1500);
                }
                
                playSuccessSound();
            }
        };
        
        recognition.onerror = function(event) {
            console.error('❌ Speech recognition error:', event.error);
            isListening = false;
            updateVoiceButton('error');
            
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
                case 'audio-capture':
                    errorMessage = '🎤 Microphone not found - Check your device';
                    break;
                default:
                    errorMessage = `❌ Voice error: ${event.error}`;
            }
            
            showVoiceStatus(errorMessage, 'error');
            playErrorSound();
        };
        
        recognition.onend = function() {
            console.log('🏁 Speech recognition ended');
            isListening = false;
            updateVoiceButton('ready');
            
            if (!isProcessing) {
                showVoiceStatus('🎤 Click microphone to speak again', 'ready');
            }
        };
    }
    
    function startStudentVoiceInput() {
        if (!recognition) {
            initStudentVoiceSystem();
            return;
        }
        
        if (isListening) {
            stopVoiceInput();
            return;
        }
        
        try {
            // Set language for recognition
            recognition.lang = studentLanguages[currentLanguage].code;
            recognition.start();
            
            showVoiceStatus('🎤 Starting voice recognition...', 'starting');
        } catch (error) {
            console.error('❌ Failed to start voice recognition:', error);
            showVoiceStatus('❌ Could not start voice input', 'error');
            playErrorSound();
        }
    }
    
    function stopVoiceInput() {
        if (recognition && isListening) {
            recognition.stop();
            showVoiceStatus('🛑 Stopping voice input...', 'stopping');
        }
    }
    
    function speakStudentText(text) {
        if (!text || !text.trim()) return;
        
        console.log('🔊 Speaking to student:', text.substring(0, 50) + '...');
        
        // Cancel any ongoing speech
        synthesis.cancel();
        
        // Clean and prepare text for students
        const cleanText = cleanTextForStudents(text);
        
        if (cleanText.length > 500) {
            // Split long text into chunks for better comprehension
            const sentences = cleanText.split(/[.!?]+/).filter(s => s.trim().length > 0);
            speakSentences(sentences, 0);
        } else {
            speakSingleText(cleanText);
        }
    }
    
    function cleanTextForStudents(text) {
        // Student-friendly text cleaning
        let clean = text
            .replace(/[🤖🎓🚀📊🧠❌🚫⚡🔥💡🎤🔊📚🌍🐳💾📄🔍🎯💪🤗✨🌟💫🏆🎮]/g, '')
            .replace(/\\*\\*(.*?)\\*\\*/g, '$1')
            .replace(/\\*(.*?)\\*/g, '$1')
            .replace(/#{1,6}\\s/g, '')
            .replace(/\\n+/g, '. ')
            .replace(/\\s+/g, ' ')
            .trim();
        
        // Make abbreviations more speech-friendly
        clean = clean
            .replace(/AI/g, 'A I')
            .replace(/API/g, 'A P I')
            .replace(/UI/g, 'U I')
            .replace(/URL/g, 'U R L')
            .replace(/PDF/g, 'P D F')
            .replace(/TTS/g, 'text to speech')
            .replace(/STT/g, 'speech to text');
        
        return clean;
    }
    
    function speakSingleText(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Enhanced settings for students
        utterance.rate = 0.85; // Slightly slower for better comprehension
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Select best voice for current language
        const voice = selectBestVoice(currentLanguage);
        if (voice) {
            utterance.voice = voice;
        }
        
        // Event handlers for student feedback
        utterance.onstart = function() {
            showVoiceStatus('🔊 AI is explaining...', 'speaking');
            updateVoiceButton('speaking');
        };
        
        utterance.onend = function() {
            showVoiceStatus('🎤 Click microphone to ask more questions', 'ready');
            updateVoiceButton('ready');
        };
        
        utterance.onerror = function(event) {
            console.error('❌ TTS error:', event.error);
            showVoiceStatus('❌ Could not speak response', 'error');
            updateVoiceButton('ready');
        };
        
        synthesis.speak(utterance);
    }
    
    function speakSentences(sentences, index) {
        if (index >= sentences.length || index >= 3) { // Limit to 3 sentences
            showVoiceStatus('🎤 Click microphone for more questions', 'ready');
            updateVoiceButton('ready');
            return;
        }
        
        const sentence = sentences[index].trim();
        if (sentence.length < 10) {
            speakSentences(sentences, index + 1);
            return;
        }
        
        const utterance = new SpeechSynthesisUtterance(sentence);
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        const voice = selectBestVoice(currentLanguage);
        if (voice) {
            utterance.voice = voice;
        }
        
        utterance.onend = function() {
            setTimeout(() => {
                speakSentences(sentences, index + 1);
            }, 500); // Small pause between sentences
        };
        
        utterance.onerror = function() {
            speakSentences(sentences, index + 1);
        };
        
        synthesis.speak(utterance);
    }
    
    function selectBestVoice(language) {
        const langCode = studentLanguages[language].code;
        const langPrefix = langCode.split('-')[0];
        
        // Find best matching voice
        let bestVoice = null;
        let fallbackVoice = null;
        
        for (let voice of voices) {
            if (voice.lang === langCode) {
                bestVoice = voice;
                break;
            }
            if (voice.lang.startsWith(langPrefix)) {
                fallbackVoice = voice;
            }
        }
        
        return bestVoice || fallbackVoice || voices[0];
    }
    
    function updateVoiceButton(state) {
        const btn = document.getElementById('student-voice-btn');
        if (!btn) return;
        
        btn.className = 'student-voice-btn';
        
        switch(state) {
            case 'listening':
                btn.className += ' listening animate-pulse';
                btn.innerHTML = '🔴';
                btn.title = 'Listening... Click to stop';
                break;
            case 'speaking':
                btn.className += ' animate-glow';
                btn.innerHTML = '🔊';
                btn.title = 'AI is speaking...';
                break;
            case 'processing':
                btn.className += ' animate-pulse';
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
                btn.title = 'Click to start voice input';
                break;
        }
    }
    
    function showVoiceStatus(message, type = 'info') {
        const statusElements = document.querySelectorAll('.voice-status');
        statusElements.forEach(element => {
            element.textContent = message;
            element.className = `voice-status ${type}`;
        });
        
        console.log(`Status (${type}):`, message);
    }
    
    function fillMessageInput(text) {
        // Find and fill the message input
        const textareas = document.querySelectorAll('textarea');
        
        for (let textarea of textareas) {
            const label = textarea.parentElement?.querySelector('label')?.textContent || '';
            const placeholder = textarea.placeholder || '';
            
            if (label.includes('Chat') || label.includes('Message') || 
                placeholder.includes('Ask') || placeholder.includes('message')) {
                
                textarea.value = text;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.focus();
                
                // Trigger visual feedback
                textarea.style.background = 'rgba(79, 172, 254, 0.2)';
                setTimeout(() => {
                    textarea.style.background = '';
                }, 1000);
                
                break;
            }
        }
    }
    
    // Audio feedback functions
    function playEncouraementSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(1200, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            // Silently fail if audio context not available
        }
    }
    
    function playSuccessSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Success chord
            oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
            oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
            oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (e) {
            // Silently fail
        }
    }
    
    function playErrorSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(300, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.2);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (e) {
            // Silently fail
        }
    }
    
    function setupAudioVisualization() {
        // Placeholder for future audio visualization
        console.log('🎵 Audio visualization setup ready');
    }
    
    // Auto-detect and speak responses
    setInterval(function() {
        // Look for TTS output
        const ttsElements = document.querySelectorAll('textarea[style*="display: none"], textarea[data-tts="true"]');
        
        for (let element of ttsElements) {
            if (element.value && element.value !== lastTTSText && element.value.length > 10) {
                lastTTSText = element.value;
                
                // Clean TTS markers
                let textToSpeak = element.value;
                if (textToSpeak.startsWith('TTS:')) {
                    textToSpeak = textToSpeak.replace('TTS:', '').trim();
                }
                
                speakStudentText(textToSpeak);
                break;
            }
        }
    }, 1500);
    
    // Language change handler
    function changeStudentLanguage(newLanguage) {
        if (studentLanguages[newLanguage]) {
            currentLanguage = newLanguage;
            console.log(`🌍 Changed to ${studentLanguages[newLanguage].name}`);
            
            if (recognition) {
                recognition.lang = studentLanguages[newLanguage].code;
            }
            
            showVoiceStatus(`🌍 Switched to ${studentLanguages[newLanguage].name} ${studentLanguages[newLanguage].flag}`, 'success');
        }
    }
    
    // Initialize when page loads
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📚 Student interface loaded');
        setTimeout(() => {
            initStudentVoiceSystem();
        }, 1000);
    });
    
    // Make functions globally available
    window.startStudentVoiceInput = startStudentVoiceInput;
    window.speakStudentText = speakStudentText;
    window.changeStudentLanguage = changeStudentLanguage;
    
    console.log('🎓 Student Voice Learning System initialized!');
    </script>
    """
    
    with gr.Blocks(css=student_css, title="🎓 AI Study Buddy - Student Edition") as app:
        
        # Header with student-friendly design
        gr.HTML("""
        <div class="student-card animate-bounce-in">
            <div style="text-align: center;">
                <h1 style="font-size: 3.5rem; margin-bottom: 15px; background: linear-gradient(45deg, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
                    🎓 AI Study Buddy
                </h1>
                <h2 style="font-size: 2rem; margin-bottom: 20px; opacity: 0.9; font-weight: 600;">
                    Your Personal Learning Companion
                </h2>
                <p style="font-size: 1.3rem; opacity: 0.8; line-height: 1.6;">
                    🧠 Smart AI Tutor • 🎤 Voice Learning • 📚 Document Analysis • 🌍 6 Languages
                </p>
            </div>
        </div>
        """)
        
        # Enhanced voice section with student-friendly design
        gr.HTML(f"""
        <div class="student-card voice-container animate-slide-up">
            <h3 style="margin-top: 0; font-size: 1.8rem; text-align: center;">🎤 Voice Learning Center</h3>
            
            <button id="student-voice-btn" class="student-voice-btn animate-float" onclick="startStudentVoiceInput()" title="Click to start voice learning">
                🎤
            </button>
            
            <div class="voice-status animate-fade-in" style="color: white; font-size: 1.3rem; font-weight: 500; text-align: center; margin: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 15px;">
                🎤 Ready for voice learning! Click the microphone to start
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 25px;">
                <div class="dashboard-item animate-fade-in" style="animation-delay: 0.2s;">
                    <div style="font-size: 1.5rem;">🇺🇸</div>
                    <div style="font-size: 0.9rem;">English</div>
                </div>
                <div class="dashboard-item animate-fade-in" style="animation-delay: 0.3s;">
                    <div style="font-size: 1.5rem;">🇮🇳</div>
                    <div style="font-size: 0.9rem;">Tamil • Hindi</div>
                </div>
                <div class="dashboard-item animate-fade-in" style="animation-delay: 0.4s;">
                    <div style="font-size: 1.5rem;">🇪🇸</div>
                    <div style="font-size: 0.9rem;">Spanish</div>
                </div>
                <div class="dashboard-item animate-fade-in" style="animation-delay: 0.5s;">
                    <div style="font-size: 1.5rem;">🇫🇷</div>
                    <div style="font-size: 0.9rem;">French</div>
                </div>
                <div class="dashboard-item animate-fade-in" style="animation-delay: 0.6s;">
                    <div style="font-size: 1.5rem;">🇩🇪</div>
                    <div style="font-size: 0.9rem;">German</div>
                </div>
            </div>
        </div>
        """)
        
        # Student login section
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML('<div class="student-card"><h3 style="margin-top: 0; font-size: 1.6rem;">🔐 Start Your Learning Journey</h3></div>')
                
                with gr.Row():
                    student_name_input = gr.Textbox(
                        label="👤 Your Name", 
                        placeholder="Enter your name (any name works!)",
                        elem_classes=["student-input"]
                    )
                    student_password_input = gr.Textbox(
                        label="🔑 Create Password", 
                        type="password", 
                        placeholder="Create any password",
                        elem_classes=["student-input"]
                    )
                    login_btn = gr.Button("🚀 Start Learning!", variant="primary", elem_classes=["student-button"])
                
                login_status = gr.HTML("""
                <div class="student-card animate-fade-in">
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">📚</div>
                        <div style="font-size: 1.2rem; font-weight: 500;">Ready to Learn Together?</div>
                        <div style="font-size: 1rem; opacity: 0.8; margin-top: 8px;">Enter any name and password to begin your study session!</div>
                    </div>
                </div>
                """)
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="student-card animate-slide-up">
                    <h4 style="color: #4facfe; margin-top: 0; font-size: 1.4rem;">✨ Learning Features</h4>
                    <div style="color: rgba(255,255,255,0.9); line-height: 1.8;">
                        <div class="dashboard-item" style="margin: 10px 0; padding: 15px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.5rem;">🤖</span>
                                <div>
                                    <div style="font-weight: 600;">AI Tutor</div>
                                    <div style="font-size: 0.85rem; opacity: 0.7;">Get instant help with any subject</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dashboard-item" style="margin: 10px 0; padding: 15px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.5rem;">🎤</span>
                                <div>
                                    <div style="font-weight: 600;">Voice Learning</div>
                                    <div style="font-size: 0.85rem; opacity: 0.7;">Speak and listen in 6 languages</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dashboard-item" style="margin: 10px 0; padding: 15px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.5rem;">📚</span>
                                <div>
                                    <div style="font-weight: 600;">Smart Documents</div>
                                    <div style="font-size: 0.85rem; opacity: 0.7;">Upload notes, get instant Q&A</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dashboard-item" style="margin: 10px 0; padding: 15px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.5rem;">💡</span>
                                <div>
                                    <div style="font-weight: 600;">Study Tips</div>
                                    <div style="font-size: 0.85rem; opacity: 0.7;">Personalized learning strategies</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """)
        
        # Main learning interface
        with gr.Row():
            with gr.Column(scale=3):
                # Student chat interface
                chatbot = gr.Chatbot(
                    height=600,
                    show_label=False,
                    elem_classes=["student-chat"]
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        label="💬 Ask Your AI Study Buddy", 
                        placeholder="Ask me anything... math, science, history, or use voice input above! 🎤",
                        lines=3,
                        scale=4,
                        elem_classes=["student-input"]
                    )
                    language_select = gr.Dropdown(
                        choices=list(STUDENT_LANGUAGES.keys()),
                        value="en",
                        label="🌍 Language",
                        scale=1,
                        elem_classes=["student-select"]
                    )
                
                with gr.Row():
                    send_btn = gr.Button("🚀 Ask Question", variant="primary", scale=2, elem_classes=["student-button"])
                    voice_chat_btn = gr.Button("🎤 Voice Question", variant="secondary", scale=1, elem_classes=["student-button"])
                    clear_btn = gr.Button("🧹 Clear Chat", variant="secondary", scale=1, elem_classes=["student-button"])
                
                # Hidden TTS output
                tts_output = gr.Textbox(
                    visible=False,
                    interactive=False,
                    elem_id="tts-output"
                )
            
            with gr.Column(scale=1):
                # Document upload section with enhanced UI
                gr.HTML('<div class="student-card"><h3 style="margin-top: 0; font-size: 1.4rem;">📚 Upload Study Materials</h3></div>')
                
                file_upload = gr.File(
                    label="📎 Drop Your Files Here",
                    file_types=[".txt", ".md", ".pdf", ".docx", ".py", ".json"],
                    file_count="multiple",
                    elem_classes=["upload-area"]
                )
                
                upload_btn = gr.Button(
                    "📤 Analyze Documents", 
                    variant="primary",
                    elem_classes=["student-button"]
                )
                
                upload_result = gr.HTML("""
                <div class="student-card animate-fade-in">
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 2.5rem; margin-bottom: 15px;">📚</div>
                        <div style="font-size: 1.1rem; font-weight: 500; margin-bottom: 10px;">Ready for Your Study Materials!</div>
                        <div style="font-size: 0.9rem; opacity: 0.8; line-height: 1.4;">
                            Upload your notes, textbooks, homework, or any study materials. I'll analyze them instantly and help you learn!
                        </div>
                        <div style="margin-top: 15px; padding: 10px; background: rgba(79, 172, 254, 0.2); border-radius: 10px;">
                            <div style="font-size: 0.85rem; opacity: 0.9;">
                                ✨ <strong>Pro Tip:</strong> Try uploading multiple files at once!
                            </div>
                        </div>
                    </div>
                </div>
                """)
                
                # Search section with enhanced UI
                gr.HTML('<div class="student-card" style="margin-top: 20px;"><h3 style="margin-top: 0; font-size: 1.4rem;">🔍 Smart Search</h3></div>')
                
                search_input = gr.Textbox(
                    label="Search Your Materials",
                    placeholder="Search for concepts, formulas, definitions...",
                    elem_classes=["student-input"]
                )
                
                search_btn = gr.Button(
                    "🔍 Find Information", 
                    variant="primary",
                    elem_classes=["student-button"]
                )
                
                search_results = gr.HTML("""
                <div class="student-card animate-fade-in">
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 2.5rem; margin-bottom: 15px;">🔍</div>
                        <div style="font-size: 1.1rem; font-weight: 500; margin-bottom: 10px;">Smart Search Ready!</div>
                        <div style="font-size: 0.9rem; opacity: 0.8; line-height: 1.4;">
                            Once you upload documents, search for any concept and I'll find relevant information instantly!
                        </div>
                    </div>
                </div>
                """)
        
        # Student motivation footer
        gr.HTML(f"""
        <div class="student-card animate-slide-up" style="margin-top: 30px;">
            <div style="text-align: center;">
                <h3 style="color: #4facfe; margin-bottom: 15px; font-size: 1.6rem;">🌟 You've Got This, Future Scholar! 🌟</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    
                    <div class="dashboard-item animate-fade-in" style="animation-delay: 0.2s;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">🚀</div>
                        <div style="font-weight: 600; margin-bottom: 5px;">Smart Learning</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">AI-powered explanations tailored just for you</div>
                    </div>
                    
                    <div class="dashboard-item animate-fade-in" style="animation-delay: 0.4s;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">🎯</div>
                        <div style="font-weight: 600; margin-bottom: 5px;">Focused Help</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Get help exactly where you need it</div>
                    </div>
                    
                    <div class="dashboard-item animate-fade-in" style="animation-delay: 0.6s;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">💫</div>
                        <div style="font-weight: 600; margin-bottom: 5px;">Always Learning</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Available 24/7 for your success</div>
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; padding: 20px; margin: 20px 0;">
                    <div style="font-style: italic; font-size: 1.2rem; font-weight: 500; margin-bottom: 10px;">
                        "The beautiful thing about learning is that no one can take it away from you." ✨
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">
                        Ready to discover something amazing today? Let's learn together! 🎓
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Add JavaScript
        gr.HTML(student_voice_js)
        
        # Event handlers with student-friendly interactions
        login_btn.click(
            fn=login_student, 
            inputs=[student_name_input, student_password_input], 
            outputs=[login_status]
        )
        
        send_btn.click(
            fn=student_chat_with_ai,
            inputs=[message_input, chatbot], 
            outputs=[chatbot, message_input, tts_output]
        )
        
        voice_chat_btn.click(
            fn=lambda msg, hist: student_chat_with_ai(msg, hist),
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, tts_output]
        )
        
        message_input.submit(
            fn=student_chat_with_ai,
            inputs=[message_input, chatbot],
            outputs=[chatbot, message_input, tts_output]
        )
        
        clear_btn.click(
            fn=clear_student_chat,
            outputs=[chatbot, message_input]
        )
        
        upload_btn.click(
            fn=process_document_upload,
            inputs=[file_upload],
            outputs=[upload_result]
        )
        
        search_btn.click(
            fn=search_student_documents,
            inputs=[search_input],
            outputs=[search_results]
        )
        
        # Language selector change handler
        language_select.change(
            fn=lambda lang: f"🌍 Switched to {STUDENT_LANGUAGES[lang]['name']} - Voice system updated!",
            inputs=[language_select],
            outputs=[]
        )
    
    return app

if __name__ == "__main__":
    logger.info("🎓 Starting Student-Friendly AI Study Buddy...")
    
    app = create_student_interface()
    
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
        print("💡 Make sure port 7860 is free and try: python student_chatbot.py")
