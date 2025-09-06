#!/usr/bin/env python3
"""
Quick Status Check for Enhanced Phase 5 System
Shows what's working and what needs to be started
"""

import requests
import subprocess
import sys
from pathlib import Path
import time

def check_process(name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', name], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def check_port(port):
    """Check if a port is in use"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def check_backend():
    """Check if backend is responding"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
    except:
        pass
    return False, {}

def main():
    print("🤖 QUANTIZED LLM CHATBOT - PHASE 5 STATUS CHECK")
    print("=" * 50)
    
    # Check directory
    if Path.cwd().name != "quantized-llm-chatbot":
        print("❌ Please run from /home/zen/quantized-llm-chatbot")
        return
    
    print("📍 Location: ✅ quantized-llm-chatbot directory")
    
    # Check virtual environment
    venv_path = Path("quantized-llm-env")
    if venv_path.exists():
        print("🐍 Virtual Environment: ✅ quantized-llm-env exists")
    else:
        print("🐍 Virtual Environment: ❌ quantized-llm-env missing")
        print("   Run: python3 -m venv quantized-llm-env")
    
    # Check enhanced files
    backend_file = Path("enhanced_backend.py")
    frontend_file = Path("enhanced_frontend.py")
    
    if backend_file.exists():
        print("🔧 Enhanced Backend: ✅ enhanced_backend.py ready")
    else:
        print("🔧 Enhanced Backend: ❌ enhanced_backend.py missing")
    
    if frontend_file.exists():
        print("🎨 Enhanced Frontend: ✅ enhanced_frontend.py ready")
    else:
        print("🎨 Enhanced Frontend: ❌ enhanced_frontend.py missing")
    
    # Check processes
    backend_running = check_process("enhanced_backend") or check_process("app.py")
    frontend_running = check_process("gradio_ui") or check_process("enhanced_frontend")
    
    print("\n📊 PROCESS STATUS:")
    print(f"🔧 Backend Process: {'✅ Running' if backend_running else '❌ Not running'}")
    print(f"🎨 Frontend Process: {'✅ Running' if frontend_running else '❌ Not running'}")
    
    # Check ports
    port_8000 = check_port(8000)
    port_7860 = check_port(7860)
    
    print("\n🌐 PORT STATUS:")
    print(f"🔧 Port 8000 (Backend): {'✅ In use' if port_8000 else '❌ Available'}")
    print(f"🎨 Port 7860 (Frontend): {'✅ In use' if port_7860 else '❌ Available'}")
    
    # Check backend health
    backend_healthy, health_data = check_backend()
    
    print("\n🤖 AI BACKEND STATUS:")
    if backend_healthy:
        print("🔧 Backend API: ✅ Responding")
        print(f"🧠 Model Loaded: {'✅ Yes' if health_data.get('model_loaded') else '❌ No'}")
        print(f"📚 Documents: {health_data.get('features', {}).get('document_count', 'Unknown')}")
    else:
        print("🔧 Backend API: ❌ Not responding")
        print("   Backend needs to be started")
    
    # Quick recommendations
    print("\n💡 QUICK ACTIONS:")
    
    if not backend_running:
        print("1️⃣  Start Backend: python enhanced_backend.py")
    
    if not frontend_running:
        print("2️⃣  Start Frontend: python enhanced_frontend.py")
    
    if backend_running and frontend_running:
        print("✅ System is running!")
        print("🌐 Frontend: http://localhost:7860")
        print("🔧 Backend API: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
    
    if not venv_path.exists():
        print("🐍 Setup Environment: chmod +x enhance_phase5.sh && ./enhance_phase5.sh")
    
    print("\n🎯 WHAT'S ENHANCED IN YOUR PHASE 5:")
    print("   ✅ Real AI responses (not just demos)")
    print("   ✅ Working document upload with RAG")
    print("   ✅ Enhanced voice with browser Speech API")
    print("   ✅ Smart document search")
    print("   ✅ Quantized model integration")
    print("   ✅ Multi-language support")

if __name__ == "__main__":
    main()