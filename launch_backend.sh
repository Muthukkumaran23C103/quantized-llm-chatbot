#!/bin/bash
echo "🚀 Starting Enhanced Phase 5 Backend..."
cd /home/zen/quantized-llm-chatbot
source quantized-llm-env/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
cd src/backend
python app.py
