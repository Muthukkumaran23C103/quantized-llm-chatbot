#!/usr/bin/env python3
"""
Launch script for Phase 5: Complete Student-Friendly Interface
"""

import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def launch_backend():
    """Launch the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    subprocess.run([
        "uvicorn", "src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

def launch_gradio():
    """Launch the Gradio interface"""
    print("🎨 Starting Gradio interface...")
    time.sleep(5)  # Wait for backend to start
    subprocess.run(["python", "src/frontend/gradio_ui.py"])

def main():
    print("""
🌟 ===================================================
    AI Study Buddy - Phase 5 Launch
    Student-Friendly Interactive Interface
🌟 ===================================================

🚀 Starting all services...
    """)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=launch_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start Gradio interface
    gradio_thread = threading.Thread(target=launch_gradio, daemon=True)
    gradio_thread.start()
    
    # Wait for services to be ready
    time.sleep(10)
    
    # Open browser tabs
    print("\n🌐 Opening browser interfaces...")
    webbrowser.open("http://localhost:8000/ui")  # Web interface
    webbrowser.open("http://localhost:7860")     # Gradio interface
    webbrowser.open("http://localhost:8000/docs") # API docs
    
    print(f"""
✅ All services are running!

🌟 Student Interfaces:
   • Modern Web UI: http://localhost:8000/ui
   • Gradio Interface: http://localhost:7860
   • API Documentation: http://localhost:8000/docs

🎯 Demo Credentials:
   • Username: admin
   • Password: secret

💡 Features Available:
   • 🤖 AI Chat with context awareness
   • 📁 Document upload with smart analysis
   • 🔍 Semantic search across materials
   • 🎨 Multiple beautiful themes
   • 📱 Mobile-responsive design
   • ⚡ Real-time responses with animations

🎓 Perfect for students learning any subject!
    """)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Study Buddy. Happy learning!")

if __name__ == "__main__":
    main()

