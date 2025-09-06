#!/bin/bash
# Enhanced Phase 5 Launcher - Building on Existing Infrastructure
# Adds working AI interaction and document upload to your quantized-llm-chatbot

echo "🤖 QUANTIZED LLM CHATBOT - PHASE 5 ENHANCED"
echo "==========================================="

cd /home/zen/quantized-llm-chatbot

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${PURPLE}🚀 Enhancing your existing Phase 5 setup...${NC}"

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
sudo fuser -k 7860/tcp 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true
pkill -f "gradio_ui.py" 2>/dev/null || true
sleep 2

# Check if in correct directory
if [ ! -d "quantized-llm-env" ]; then
    echo -e "${RED}❌ quantized-llm-env not found. Creating new environment...${NC}"
    python3 -m venv quantized-llm-env
fi

# Activate environment
source quantized-llm-env/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Install enhanced dependencies for AI interaction
echo -e "${BLUE}📦 Installing AI backend dependencies...${NC}"

cat > requirements_enhanced.txt << 'EOF'
# Core framework
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
gradio>=4.7.1
pydantic>=2.5.0

# AI/ML for quantized models
torch>=2.0.0
transformers>=4.35.0
sentence-transformers>=2.2.0

# Language processing
langdetect>=1.0.9
googletrans==4.0.0

# API and utilities
requests>=2.31.0
python-multipart>=0.0.6
python-dotenv>=1.0.0

# Optional voice (if available)
# speechrecognition>=3.10.0
# pyttsx3>=2.90
EOF

pip install --upgrade pip setuptools wheel
pip install -r requirements_enhanced.txt

# Setup enhanced directory structure
echo -e "${YELLOW}📁 Setting up enhanced project structure...${NC}"

# Create directories if they don't exist
mkdir -p src/{backend,frontend,services,utils}
mkdir -p data/{documents,models,vectorstore}
mkdir -p logs

# Copy enhanced files to your existing structure
echo -e "${BLUE}📋 Installing enhanced components...${NC}"

# Install enhanced backend
cp enhanced_backend.py src/backend/app.py

# Install enhanced frontend (backup existing first)
if [ -f "src/frontend/gradio_ui.py" ]; then
    cp src/frontend/gradio_ui.py src/frontend/gradio_ui_backup.py
    echo -e "${YELLOW}📋 Backed up existing gradio_ui.py${NC}"
fi
cp enhanced_frontend.py src/frontend/gradio_ui.py

# Create launch scripts
cat > launch_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Enhanced Phase 5 Backend..."
cd /home/zen/quantized-llm-chatbot
source quantized-llm-env/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
cd src/backend
python app.py
EOF

cat > launch_frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 Starting Enhanced Phase 5 Frontend..."
cd /home/zen/quantized-llm-chatbot
source quantized-llm-env/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
cd src/frontend
python gradio_ui.py
EOF

chmod +x launch_backend.sh launch_frontend.sh

echo ""
echo -e "${GREEN}🎉 PHASE 5 ENHANCEMENT COMPLETE!${NC}"
echo -e "${PURPLE}================================${NC}"
echo ""
echo -e "${BLUE}📋 What's Enhanced:${NC}"
echo -e "${GREEN}   ✅ Working AI interaction with quantized models${NC}"
echo -e "${GREEN}   ✅ Document upload and RAG processing${NC}"
echo -e "${GREEN}   ✅ Enhanced voice system with browser APIs${NC}"
echo -e "${GREEN}   ✅ Smart search across uploaded documents${NC}"
echo -e "${GREEN}   ✅ Backend-frontend integration${NC}"
echo -e "${GREEN}   ✅ Model status monitoring${NC}"
echo ""
echo -e "${YELLOW}🚀 LAUNCH OPTIONS:${NC}"
echo ""
echo -e "${BLUE}Option 1 - Full System (Recommended):${NC}"
echo "1️⃣  In terminal 1: ./launch_backend.sh"
echo "2️⃣  In terminal 2: ./launch_frontend.sh"
echo ""
echo -e "${BLUE}Option 2 - Quick Launch:${NC}"
echo "./launch_backend.sh & sleep 5 && ./launch_frontend.sh"
echo ""
echo -e "${BLUE}Option 3 - Step by Step:${NC}"
echo "Backend:  python src/backend/app.py"
echo "Frontend: python src/frontend/gradio_ui.py"
echo ""
echo -e "${PURPLE}🌐 Access URLs:${NC}"
echo -e "${GREEN}   Frontend: http://localhost:7860${NC}"
echo -e "${GREEN}   Backend:  http://localhost:8000${NC}"
echo -e "${GREEN}   API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}🧠 AI FEATURES:${NC}"
echo -e "${GREEN}   🤖 Real quantized model responses (not just demos)${NC}"
echo -e "${GREEN}   📚 Working document upload with RAG${NC}"
echo -e "${GREEN}   🔍 Smart search across your documents${NC}"
echo -e "${GREEN}   🎤 Enhanced voice with speech recognition${NC}"
echo -e "${GREEN}   🌍 Multi-language support${NC}"
echo ""
echo -e "${BLUE}📖 Quick Start Guide:${NC}"
echo -e "${GREEN}1. Launch backend first: ./launch_backend.sh${NC}"
echo -e "${GREEN}2. Wait for 'Models loaded' message${NC}"
echo -e "${GREEN}3. Launch frontend: ./launch_frontend.sh${NC}"
echo -e "${GREEN}4. Go to http://localhost:7860${NC}"
echo -e "${GREEN}5. Login with any username/password${NC}"
echo -e "${GREEN}6. Start chatting with your quantized AI!${NC}"
echo ""

# Optionally start the system
echo -e "${YELLOW}🤔 Start the enhanced system now? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}🚀 Starting Enhanced Phase 5 System...${NC}"
    echo ""
    echo -e "${BLUE}Starting backend in background...${NC}"
    ./launch_backend.sh > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo -e "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
    sleep 8
    
    echo -e "${BLUE}Starting frontend...${NC}"
    ./launch_frontend.sh &
    FRONTEND_PID=$!
    
    echo ""
    echo -e "${GREEN}🎉 ENHANCED PHASE 5 SYSTEM RUNNING!${NC}"
    echo -e "${PURPLE}====================================${NC}"
    echo ""
    echo -e "${GREEN}🌐 Frontend: http://localhost:7860${NC}"
    echo -e "${GREEN}🔧 Backend:  http://localhost:8000${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Cleanup function
    cleanup() {
        echo ""
        echo -e "${YELLOW}🛑 Shutting down Enhanced Phase 5...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        pkill -f "app.py" 2>/dev/null || true
        pkill -f "gradio_ui.py" 2>/dev/null || true
        echo -e "${GREEN}✅ All services stopped${NC}"
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM
    
    # Keep running
    wait
else
    echo -e "${BLUE}📋 Manual launch when ready:${NC}"
    echo -e "${GREEN}   ./launch_backend.sh & ./launch_frontend.sh${NC}"
fi