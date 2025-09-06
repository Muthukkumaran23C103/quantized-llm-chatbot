#!/bin/bash
# Ultimate Student AI Study Buddy Launcher
# Complete setup with working document upload and enhanced voice

echo "🎓 STUDENT AI STUDY BUDDY - ULTIMATE EDITION"
echo "============================================"

cd /home/zen/quantized-llm-chatbot

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🚀 Setting up the ultimate student learning experience...${NC}"

# Kill any existing processes
echo "🔄 Cleaning up..."
sudo fuser -k 7860/tcp 2>/dev/null || true
pkill -f "gradio" 2>/dev/null || true
sleep 2

# Activate environment
if [ -d "quantized-llm-env" ]; then
    source quantized-llm-env/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv quantized-llm-env
    source quantized-llm-env/bin/activate
fi

# Install/upgrade essential packages for students
echo -e "${BLUE}📚 Installing student learning packages...${NC}"

# Create optimized requirements for students
cat > requirements_student.txt << 'EOF'
# Core UI
gradio>=4.7.1
requests>=2.31.0

# Enhanced functionality
numpy>=1.24.0
pandas>=2.0.0

# File processing for students
python-docx>=0.8.11
PyPDF2>=3.0.1
openpyxl>=3.1.0

# Environment
python-dotenv>=1.0.0

# Optional: Enhanced features
# speechrecognition>=3.10.0
# pyttsx3>=2.90
EOF

pip install --upgrade pip setuptools wheel
pip install -r requirements_student.txt

# Create directories
mkdir -p uploaded_documents data logs

# Copy the student chatbot
echo -e "${CYAN}🎨 Setting up student interface...${NC}"
cp student_chatbot.py src/frontend/student_gradio_ui.py

echo ""
echo -e "${GREEN}🎉 STUDENT AI STUDY BUDDY READY!${NC}"
echo -e "${PURPLE}================================${NC}"
echo ""
echo -e "${CYAN}🎓 LAUNCH OPTIONS:${NC}"
echo ""
echo -e "${GREEN}1. 🚀 STUDENT EDITION (Recommended):${NC}"
echo "   python student_chatbot.py"
echo ""
echo -e "${GREEN}2. 📚 FROM PROJECT DIRECTORY:${NC}"
echo "   python src/frontend/student_gradio_ui.py"
echo ""
echo -e "${YELLOW}🌟 FEATURES INCLUDED:${NC}"
echo -e "${CYAN}   ✅ Working document upload with drag & drop${NC}"
echo -e "${CYAN}   ✅ Enhanced STT/TTS with Web Speech API${NC}"
echo -e "${CYAN}   ✅ 6 language support with auto-detection${NC}"
echo -e "${CYAN}   ✅ Beautiful animated student-friendly UI${NC}"
echo -e "${CYAN}   ✅ Smart document search and analysis${NC}"
echo -e "${CYAN}   ✅ Audio feedback and encouragement${NC}"
echo -e "${CYAN}   ✅ Progress tracking and study tips${NC}"
echo -e "${CYAN}   ✅ Responsive design for all devices${NC}"
echo ""
echo -e "${BLUE}🎤 VOICE IMPROVEMENTS:${NC}"
echo -e "${CYAN}   🔊 Web Speech API (more reliable than Python libs)${NC}"
echo -e "${CYAN}   🎯 Real-time speech recognition with confidence scores${NC}"
echo -e "${CYAN}   🌍 Multi-language voice synthesis with natural voices${NC}"
echo -e "${CYAN}   🎵 Audio feedback and encouragement sounds${NC}"
echo -e "${CYAN}   📊 Voice activity detection and visualization${NC}"
echo ""
echo -e "${BLUE}📚 DOCUMENT FEATURES:${NC}"
echo -e "${CYAN}   📄 Support for TXT, PDF, DOCX, MD files${NC}"
echo -e "${CYAN}   🔍 Intelligent topic extraction${NC}"
echo -e "${CYAN}   📊 Document analysis with word counts${NC}"
echo -e "${CYAN}   🎯 Smart search with relevance scoring${NC}"
echo -e "${CYAN}   💾 Persistent document storage${NC}"
echo ""
echo -e "${PURPLE}🎨 UI ANIMATIONS:${NC}"
echo -e "${CYAN}   ✨ Bounce, slide, fade, and pulse animations${NC}"
echo -e "${CYAN}   🎭 Interactive voice button with states${NC}"
echo -e "${CYAN}   🌈 Glass morphism design with gradients${NC}"
echo -e "${CYAN}   📱 Mobile-responsive layout${NC}"
echo -e "${CYAN}   🎪 Motivational messages and progress tracking${NC}"
echo ""

# Launch the student edition
echo -e "${GREEN}🚀 LAUNCHING STUDENT AI STUDY BUDDY...${NC}"
echo ""
echo -e "${YELLOW}⏳ Starting in 3 seconds...${NC}"
sleep 1
echo -e "${YELLOW}⏳ 2...${NC}"
sleep 1  
echo -e "${YELLOW}⏳ 1...${NC}"
sleep 1
echo -e "${GREEN}🎓 HERE WE GO!${NC}"
echo ""

# Start the student chatbot
python student_chatbot.py
