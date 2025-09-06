#!/usr/bin/env python3

import asyncio
import time
from src.inference.ollama.client import OllamaClient, ModelConfig

async def benchmark_model(client: OllamaClient, model_name: str, prompt: str):
    """Benchmark a model's performance"""
    print(f"\n🔍 Benchmarking {model_name}")
    
    # Ensure model is available
    models = await client.list_models()
    if model_name not in [m['name'] for m in models]:
        print(f"⚠️  Model {model_name} not available")
        return
    
    config = ModelConfig(name=model_name, max_tokens=100)
    
    # Warmup
    print("   Warming up...")
    client.generate_sync(model_name, "Hello", config)
    
    # Benchmark
    start_time = time.time()
    response = client.generate_sync(model_name, prompt, config)
    end_time = time.time()
    
    duration = end_time - start_time
    tokens = len(response.split())
    tokens_per_sec = tokens / duration if duration > 0 else 0
    
    print(f"   ✅ Generated {tokens} tokens in {duration:.2f}s")
    print(f"   ⚡ Speed: {tokens_per_sec:.1f} tokens/sec")
    print(f"   📝 Response: {response[:100]}...")

async def main():
    client = OllamaClient()
    
    if not await client.health_check():
        print("❌ Ollama not running")
        return
    
    models_to_test = [
        "tinyllama:1.1b-chat-q4_0",
        "phi:2.7b-chat-fp16", 
        "mistral:7b-instruct-v0.1-q4_K_M"
    ]
    
    prompt = "Explain quantum computing in simple terms."
    
    print("🚀 Starting model benchmarks")
    print(f"📊 Prompt: {prompt}")
    
    for model in models_to_test:
        await benchmark_model(client, model, prompt)
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
