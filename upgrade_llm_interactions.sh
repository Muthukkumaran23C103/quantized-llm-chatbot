#!/bin/bash
# UPGRADE LLM INTERACTIONS - Much Better AI Responses
# Replaces your current backend with enhanced models and prompting

echo "🧠 UPGRADING YOUR LLM FOR MUCH BETTER AI INTERACTIONS"
echo "==================================================="

cd /home/zen/quantized-llm-chatbot

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔄 Step 1: Stopping current backend...${NC}"
# Kill existing backend
sudo fuser -k 8000/tcp 2>/dev/null || true
pkill -f "backend" 2>/dev/null || true
pkill -f "enhanced_backend" 2>/dev/null || true
sleep 3

echo -e "${BLUE}📦 Step 2: Installing better model packages...${NC}"
# Activate environment
source quantized-llm-env/bin/activate

# Install better packages for enhanced models
pip install --upgrade transformers torch accelerate sentence-transformers

echo -e "${BLUE}🧠 Step 3: Setting up MUCH better models...${NC}"

# Backup current backend
if [ -f "enhanced_backend.py" ]; then
    cp enhanced_backend.py enhanced_backend_backup.py
    echo "📋 Backed up current backend"
fi

# Copy the enhanced LLM backend
cp enhanced_llm_backend.py enhanced_backend.py

echo -e "${BLUE}🎯 Step 4: Testing enhanced backend...${NC}"

# Start enhanced backend in background to test
python enhanced_backend.py > logs/enhanced_backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${YELLOW}⏳ Testing enhanced backend startup...${NC}"
sleep 10

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Enhanced backend is running!${NC}"
    
    # Get model info
    echo -e "${BLUE}🧠 Checking loaded model...${NC}"
    MODEL_INFO=$(curl -s http://localhost:8000/models/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('loaded'):
        model_info = data.get('model_info', {})
        print(f\"✅ Model: {model_info.get('name', 'Unknown')} ({model_info.get('size', 'Unknown size')}) - Quality: {model_info.get('quality', 'Unknown')}\")
        print(f\"✅ Device: {data.get('device', 'Unknown')}\")
        print(f\"✅ Enhancement Level: {data.get('enhancement_level', 'Basic')}\")
    else:
        print('⚠️ Models still loading...')
except:
    print('⚠️ Could not get model info')
" 2>/dev/null)
    
    echo "$MODEL_INFO"
    
    # Stop test backend
    kill $BACKEND_PID 2>/dev/null || true
    sleep 2
    
    echo ""
    echo -e "${GREEN}🎉 LLM UPGRADE COMPLETE!${NC}"
    echo -e "${BLUE}=========================${NC}"
    echo ""
    echo -e "${GREEN}✅ MUCH Better AI Interactions:${NC}"
    echo "   • Better model selection (DialoGPT-medium, GPT-2, BLOOM)"
    echo "   • Enhanced prompt engineering for clearer responses"
    echo "   • Improved generation parameters (temperature, top_p, repetition_penalty)"
    echo "   • Context-aware conversations that remember previous exchanges"
    echo "   • Smart fallback responses instead of generic ones"
    echo "   • Better document analysis and search"
    echo ""
    echo -e "${GREEN}🧠 Model Improvements:${NC}"
    echo "   • DialoGPT-medium (355M) for conversational AI"
    echo "   • Enhanced prompting with system instructions"
    echo "   • Better response cleaning and formatting"
    echo "   • Conversation memory and context awareness"
    echo ""
    echo -e "${YELLOW}🚀 Launch Your Enhanced System:${NC}"
    echo ""
    echo -e "${GREEN}Terminal 1:${NC} python enhanced_backend.py"
    echo -e "${GREEN}Terminal 2:${NC} python FIXED_ultimate_chatbot.py"
    echo ""
    echo -e "${BLUE}Or use auto-launch:${NC}"
    
    read -p "Start the enhanced system now? (y/n): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}🚀 Starting Enhanced LLM Backend...${NC}"
        python enhanced_backend.py > logs/enhanced_backend.log 2>&1 &
        BACKEND_PID=$!
        
        echo -e "${YELLOW}⏳ Waiting for models to load...${NC}"
        sleep 12
        
        echo -e "${BLUE}🎨 Starting Frontend...${NC}"
        python FIXED_ultimate_chatbot.py &
        FRONTEND_PID=$!
        
        echo ""
        echo -e "${GREEN}🎉 ENHANCED SYSTEM RUNNING!${NC}"
        echo -e "${GREEN}=========================${NC}"
        echo ""
        echo -e "${GREEN}🌐 Frontend: http://localhost:7860${NC}"
        echo -e "${GREEN}🔧 Backend:  http://localhost:8000${NC}"
        echo ""
        echo -e "${YELLOW}🧠 The AI interactions are now MUCH better!${NC}"
        echo -e "${YELLOW}   • More natural conversations${NC}"
        echo -e "${YELLOW}   • Better understanding of context${NC}"  
        echo -e "${YELLOW}   • More informative responses${NC}"
        echo -e "${YELLOW}   • Improved topic handling${NC}"
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        
        # Cleanup function
        cleanup() {
            echo ""
            echo -e "${YELLOW}🛑 Stopping enhanced system...${NC}"
            kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
            sudo fuser -k 8000/tcp 2>/dev/null || true
            sudo fuser -k 7860/tcp 2>/dev/null || true
            echo -e "${GREEN}✅ Enhanced system stopped${NC}"
            exit 0
        }
        
        trap cleanup SIGINT SIGTERM
        wait
    else
        echo ""
        echo -e "${BLUE}📋 Manual Launch:${NC}"
        echo -e "${GREEN}   python enhanced_backend.py${NC}"
        echo -e "${GREEN}   python FIXED_ultimate_chatbot.py${NC}"
    fi
    
else
    echo -e "${RED}❌ Enhanced backend failed to start${NC}"
    echo -e "${YELLOW}💡 Try installing missing packages:${NC}"
    echo "   pip install transformers torch accelerate sentence-transformers"
    
    # Stop failed backend
    kill $BACKEND_PID 2>/dev/null || true
fi