#!/bin/bash
echo "🎨 Starting Enhanced Phase 5 Frontend..."
cd /home/zen/quantized-llm-chatbot
source quantized-llm-env/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
cd src/frontend
python gradio_ui.py
