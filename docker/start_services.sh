#!/bin/bash

# Startup script for Ollama + FastAPI container

set -e

echo "🚀 Starting Ollama + FastAPI services..."

# Start Ollama server in background
echo "📦 Starting Ollama server..."
ollama serve &

# Wait for Ollama to start
echo "⏳ Waiting for Ollama server to be ready..."
until curl -f http://localhost:11434/ > /dev/null 2>&1; do
    sleep 2
    echo "   Still waiting for Ollama..."
done

echo "✅ Ollama server is ready"

# Download default models if they don't exist
echo "🔍 Checking for required models..."

# Check if TinyLLaMA is available (fastest to download)
if ! ollama list | grep -q "tinyllama"; then
    echo "📥 Downloading TinyLLaMA model..."
    ollama pull tinyllama:1.1b-chat-q4_0
fi

# Optionally download Mistral (commented out for faster startup)
# echo "📥 Downloading Mistral 7B model..."
# ollama pull mistral:7b-instruct-v0.1-q4_K_M

echo "✅ Models ready"

# Start FastAPI application
echo "🌐 Starting FastAPI application..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
