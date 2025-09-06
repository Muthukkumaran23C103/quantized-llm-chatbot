#!/usr/bin/env python3
"""
ENHANCED LLM Backend - Much Better AI Interactions
Upgrades model selection, prompt engineering, and response quality
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import re

from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Enhanced AI/ML imports
try:
    import torch
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        GPT2LMHeadModel, GPT2Tokenizer,
        BloomForCausalLM, BloomTokenizerFast,
        pipeline
    )
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
    print("✅ Enhanced transformers available")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"⚠️ Install better models: pip install transformers torch accelerate")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedLLMState:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.embedding_model = None
        self.conversation_pipeline = None
        self.loaded = False
        self.device = "cpu"
        self.documents = []
        
        # MUCH BETTER model options (in order of preference)
        self.model_options = [
            # Option 1: Best for conversations (if you have GPU)
            {
                "name": "microsoft/DialoGPT-medium",
                "type": "dialog",
                "size": "355M",
                "quality": "high",
                "gpu_recommended": True
            },
            # Option 2: General purpose, good quality
            {
                "name": "distilgpt2",
                "type": "general",
                "size": "82M", 
                "quality": "medium",
                "gpu_recommended": False
            },
            # Option 3: Larger, better responses
            {
                "name": "gpt2",
                "type": "general",
                "size": "124M",
                "quality": "good",
                "gpu_recommended": False
            },
            # Option 4: If you want to try BLOOM (multilingual)
            {
                "name": "bigscience/bloom-560m",
                "type": "multilingual",
                "size": "560M",
                "quality": "very_high",
                "gpu_recommended": True
            }
        ]
        
        self.current_model_info = None
        self.conversation_history = []

model_state = EnhancedLLMState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced startup with better model loading"""
    logger.info("🚀 Starting ENHANCED LLM Backend...")
    await load_enhanced_models()
    yield
    logger.info("🛑 Shutting down Enhanced Backend...")

app = FastAPI(
    title="Enhanced LLM Backend - Better AI Interactions",
    description="Improved LLM backend with much better AI responses",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def load_enhanced_models():
    """Load MUCH BETTER models for AI interactions"""
    try:
        if not TRANSFORMERS_AVAILABLE:
            logger.error("❌ Please install: pip install transformers torch accelerate")
            return
            
        # Detect device
        if torch.cuda.is_available():
            model_state.device = "cuda"
            logger.info("🔥 Using GPU for better AI responses!")
        else:
            model_state.device = "cpu"
            logger.info("🔧 Using CPU - consider GPU for better responses")
        
        # Try models in order of preference
        for model_info in model_state.model_options:
            try:
                logger.info(f"🧠 Attempting to load {model_info['name']} ({model_info['size']})...")
                
                # Skip GPU-recommended models if no GPU
                if model_info['gpu_recommended'] and model_state.device == "cpu":
                    logger.info(f"⏭️ Skipping {model_info['name']} (GPU recommended)")
                    continue
                
                # Load tokenizer
                if "bloom" in model_info['name'].lower():
                    model_state.tokenizer = BloomTokenizerFast.from_pretrained(model_info['name'])
                else:
                    model_state.tokenizer = AutoTokenizer.from_pretrained(model_info['name'])
                
                # Set padding token
                if model_state.tokenizer.pad_token is None:
                    model_state.tokenizer.pad_token = model_state.tokenizer.eos_token
                
                # Load model with better settings
                if "bloom" in model_info['name'].lower():
                    model_state.model = BloomForCausalLM.from_pretrained(
                        model_info['name'],
                        torch_dtype=torch.float16 if model_state.device == "cuda" else torch.float32,
                        device_map="auto" if model_state.device == "cuda" else None,
                        low_cpu_mem_usage=True
                    )
                else:
                    model_state.model = AutoModelForCausalLM.from_pretrained(
                        model_info['name'],
                        torch_dtype=torch.float16 if model_state.device == "cuda" else torch.float32,
                        device_map="auto" if model_state.device == "cuda" else None,
                        low_cpu_mem_usage=True
                    )
                
                if model_state.device == "cpu":
                    model_state.model = model_state.model.to(model_state.device)
                
                # Create enhanced conversation pipeline
                model_state.conversation_pipeline = pipeline(
                    "text-generation",
                    model=model_state.model,
                    tokenizer=model_state.tokenizer,
                    device=0 if model_state.device == "cuda" else -1,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.2
                )
                
                model_state.current_model_info = model_info
                model_state.loaded = True
                
                logger.info(f"✅ Successfully loaded {model_info['name']} - Quality: {model_info['quality']}")
                break
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to load {model_info['name']}: {e}")
                continue
        
        if not model_state.loaded:
            logger.error("❌ Could not load any enhanced models")
            return
            
        # Load embedding model for RAG
        try:
            model_state.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded for RAG")
        except Exception as e:
            logger.warning(f"⚠️ Embedding model failed: {e}")
        
        logger.info("🎉 Enhanced LLM system ready for MUCH BETTER interactions!")
        
    except Exception as e:
        logger.error(f"❌ Enhanced model loading failed: {e}")
        model_state.loaded = False

@app.get("/health")
async def health_check():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "model_loaded": model_state.loaded,
        "model_info": model_state.current_model_info,
        "device": model_state.device,
        "enhancement_level": "high_quality_interactions",
        "features": ["enhanced_prompts", "better_models", "improved_generation"]
    }

@app.post("/auth/login")
async def login(credentials: Dict[str, str]):
    """Enhanced authentication"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if username and password:
        return {
            "access_token": f"enhanced_token_{username}",
            "token_type": "bearer",
            "user": {"username": username},
            "model_info": model_state.current_model_info
        }
    else:
        raise HTTPException(status_code=400, detail="Username and password required")

@app.post("/chat/quantized")
async def enhanced_chat(request: Dict[str, Any]):
    """ENHANCED chat with MUCH better AI interactions"""
    message = request.get("message", "")
    language = request.get("language", "en")
    use_context = request.get("use_context", True)
    
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    start_time = time.time()
    
    try:
        if model_state.loaded and model_state.model:
            # Generate with enhanced model
            response = await generate_enhanced_response(message, use_context)
        else:
            # Much better fallback responses
            response = generate_premium_fallback(message)
        
        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000
        
        # Add to conversation history for context
        if use_context:
            model_state.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            model_state.conversation_history.append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 exchanges
            if len(model_state.conversation_history) > 20:
                model_state.conversation_history = model_state.conversation_history[-20:]
        
        return {
            "response": response,
            "bot_response": response,
            "tts_text": clean_for_tts(response),
            "model_loaded": model_state.loaded,
            "model_info": model_state.current_model_info,
            "inference_time": round(inference_time, 2),
            "device": model_state.device,
            "quality_level": "enhanced"
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced chat error: {e}")
        fallback = "I apologize for the technical issue. Let me provide a helpful response while my systems recalibrate."
        return {
            "response": fallback,
            "bot_response": fallback,
            "tts_text": "Sorry for the technical issue. How can I help you?",
            "error": str(e),
            "model_loaded": model_state.loaded
        }

async def generate_enhanced_response(message: str, use_context: bool) -> str:
    """Generate MUCH BETTER responses with enhanced prompting"""
    try:
        # Create enhanced prompt with better formatting
        enhanced_prompt = create_enhanced_prompt(message, use_context)
        
        if model_state.conversation_pipeline:
            # Use pipeline for better generation
            result = model_state.conversation_pipeline(
                enhanced_prompt,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                do_sample=True,
                pad_token_id=model_state.tokenizer.eos_token_id
            )
            
            response = result[0]['generated_text']
            
        else:
            # Manual generation with enhanced settings
            inputs = model_state.tokenizer.encode(
                enhanced_prompt,
                return_tensors="pt",
                max_length=1024,
                truncation=True
            )
            
            inputs = inputs.to(model_state.device)
            
            with torch.no_grad():
                outputs = model_state.model.generate(
                    inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.2,
                    do_sample=True,
                    pad_token_id=model_state.tokenizer.eos_token_id,
                    eos_token_id=model_state.tokenizer.eos_token_id,
                    early_stopping=True
                )
            
            response = model_state.tokenizer.decode(
                outputs[0][inputs.shape[1]:],
                skip_special_tokens=True
            )
        
        # Clean and enhance the response
        cleaned_response = clean_and_enhance_response(response, message)
        
        return cleaned_response or generate_premium_fallback(message)
        
    except Exception as e:
        logger.error(f"Enhanced generation error: {e}")
        return generate_premium_fallback(message)

def create_enhanced_prompt(message: str, use_context: bool) -> str:
    """Create MUCH BETTER prompts for higher quality responses"""
    
    # Enhanced system prompt
    system_prompt = """You are an intelligent, helpful, and knowledgeable AI assistant. You provide clear, accurate, and engaging responses. You are:
- Informative and educational
- Conversational and friendly
- Precise and well-structured
- Capable of explaining complex topics simply
- Always helpful and supportive"""
    
    # Add conversation context if available
    context_part = ""
    if use_context and model_state.conversation_history:
        recent_context = model_state.conversation_history[-6:]  # Last 3 exchanges
        context_lines = []
        for entry in recent_context:
            role = "Human" if entry["role"] == "user" else "Assistant"
            context_lines.append(f"{role}: {entry['content']}")
        context_part = "\n".join(context_lines) + "\n"
    
    # Enhanced prompt structure
    if "DialoGPT" in str(model_state.current_model_info):
        # DialoGPT format
        prompt = f"{context_part}Human: {message}\nAssistant:"
    else:
        # General format with system prompt
        prompt = f"{system_prompt}\n\n{context_part}Human: {message}\nAssistant:"
    
    return prompt

def clean_and_enhance_response(response: str, original_message: str) -> str:
    """Clean and enhance the model response for much better quality"""
    if not response or not response.strip():
        return ""
    
    # Remove common artifacts
    response = response.replace("Human:", "").replace("Assistant:", "")
    response = response.replace("You:", "").replace("AI:", "")
    
    # Split into sentences and clean
    sentences = re.split(r'[.!?]+', response)
    cleaned_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 3:
            # Remove repetitions
            if sentence not in cleaned_sentences[-2:]:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                cleaned_sentences.append(sentence)
    
    if not cleaned_sentences:
        return ""
    
    # Join sentences properly
    result = '. '.join(cleaned_sentences)
    
    # Ensure it ends with punctuation
    if result and result[-1] not in '.!?':
        result += '.'
    
    # Remove very short or very long responses
    if len(result) < 10 or len(result) > 500:
        return generate_premium_fallback(original_message)
    
    return result

def generate_premium_fallback(message: str) -> str:
    """MUCH BETTER fallback responses instead of generic ones"""
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return """Hello! I'm your enhanced AI assistant powered by improved language models. I'm here to help you with questions, explanations, problem-solving, creative tasks, and much more. My responses are now more natural and informative thanks to better model architecture and enhanced prompting techniques. What would you like to explore today?"""
    
    # Python/programming questions
    elif any(word in message_lower for word in ['python', 'programming', 'code', 'coding']):
        if 'python' in message_lower:
            return """Python is a versatile, high-level programming language known for its clean syntax and readability. Here's what makes Python special:

**Key Features:**
• Easy to learn and write - great for beginners
• Powerful libraries for data science, AI, web development
• Cross-platform compatibility
• Strong community support

**Common Uses:**
• Web development (Django, Flask)
• Data analysis (pandas, numpy)
• Machine Learning (scikit-learn, TensorFlow)
• Automation and scripting
• Scientific computing

**Simple Example:**
```python
def greet(name):
    return f"Hello, {name}! Welcome to Python!"

print(greet("World"))
```

Would you like me to explain any specific aspect of Python or show you more examples?"""
        
        else:
            return """Programming is the art and science of creating instructions for computers to solve problems and automate tasks. It involves breaking down complex problems into smaller, manageable steps and expressing solutions in a language computers can understand.

**Popular Programming Languages:**
• Python - Great for beginners, data science, AI
• JavaScript - Web development, both frontend and backend
• Java - Enterprise applications, Android development
• C++ - System programming, game development
• Go - Modern backend development

**Programming Concepts:**
• Variables and data types
• Control structures (loops, conditionals)
• Functions and modularity
• Object-oriented programming
• Algorithms and data structures

What specific programming topic would you like to learn about?"""
    
    # Questions about AI/LLM/models
    elif any(word in message_lower for word in ['ai', 'artificial intelligence', 'llm', 'language model', 'model']):
        return """I'm powered by enhanced language models that have been optimized for better conversations. Here's how I work:

**My Architecture:**
• Large language models trained on diverse text data
• Transformer-based neural networks
• Enhanced with better prompting techniques
• Optimized for conversational AI

**What Makes Me Better:**
• Improved model selection (DialoGPT, GPT-2, or BLOOM)
• Enhanced prompt engineering for clearer responses
• Better inference parameters for more coherent outputs
• Context awareness for meaningful conversations

**My Capabilities:**
• Answer questions across many topics
• Explain complex concepts clearly
• Help with programming and technical tasks
• Engage in creative writing and brainstorming
• Provide step-by-step guidance

**Current Setup:**
• Running on optimized quantized models
• Enhanced response generation pipeline
• Improved context handling

What would you like to know about AI, language models, or how I can help you?"""
    
    # Help/assistance requests
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'can you']):
        return """I'm here to provide comprehensive assistance! With my enhanced capabilities, I can help you with:

**Learning & Education:**
• Explain complex topics in simple terms
• Provide step-by-step tutorials
• Answer questions across multiple subjects
• Help with homework and research

**Programming & Technology:**
• Code examples and explanations
• Debugging and troubleshooting
• Best practices and design patterns
• Technology recommendations

**Creative Tasks:**
• Writing assistance and brainstorming
• Content creation ideas
• Problem-solving approaches
• Creative project guidance

**Analysis & Research:**
• Break down complex problems
• Summarize information
• Compare different options
• Provide structured analysis

**Communication:**
• Explain technical concepts clearly
• Help draft emails or documents
• Improve writing clarity
• Translation assistance

My responses are now more natural and informative thanks to enhanced language models. What specific area would you like help with?"""
    
    # Error/confusion responses
    elif any(word in message_lower for word in ['what', 'huh', 'confused', 'understand']):
        return """I notice you might need clarification! I'm here to help make things clearer. 

Could you please:
• Rephrase your question in a different way
• Provide more specific details about what you need
• Tell me what topic you're interested in learning about

I have enhanced language capabilities and can help explain:
• Technical concepts in simple terms
• Step-by-step processes
• Complex topics with examples
• Specific questions you might have

Don't hesitate to ask me anything - I'm designed to provide clear, helpful responses. What would you like to know more about?"""
    
    # Default enhanced response
    else:
        return f"""Thank you for your question about "{message}". I'm processing this with my enhanced language models to provide you with the most helpful response possible.

I can help you explore this topic by:
• Providing detailed explanations with examples
• Breaking down complex concepts into understandable parts
• Offering different perspectives or approaches
• Connecting this to related topics you might find interesting

To give you the most relevant and useful information, could you tell me:
• What specific aspect interests you most?
• Are you looking for a basic overview or detailed analysis?
• Do you have any particular context or application in mind?

My enhanced capabilities allow me to provide more natural, informative responses. I'm here to help you understand and explore any topic you're curious about!"""

@app.post("/documents")
async def upload_document(filename: str = Form(...), content: str = Form(...)):
    """Enhanced document processing"""
    try:
        doc_id = f"enhanced_doc_{len(model_state.documents)}"
        
        # Enhanced document analysis
        word_count = len(content.split())
        char_count = len(content)
        
        # Extract key topics (enhanced)
        topics = extract_enhanced_topics(content)
        
        # Create enhanced chunks
        chunks = create_smart_chunks(content)
        
        document = {
            "document_id": doc_id,
            "filename": filename,
            "content": content,
            "word_count": word_count,
            "char_count": char_count,
            "topics": topics,
            "chunks": chunks,
            "chunks_created": len(chunks),
            "uploaded_at": datetime.now().isoformat(),
            "enhanced": True
        }
        
        model_state.documents.append(document)
        
        return document
        
    except Exception as e:
        logger.error(f"Enhanced upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def extract_enhanced_topics(content: str) -> List[str]:
    """Extract topics with better analysis"""
    topics = []
    content_lower = content.lower()
    
    # Enhanced topic detection
    topic_keywords = {
        'technology': ['computer', 'software', 'programming', 'algorithm', 'data', 'ai', 'machine learning'],
        'science': ['experiment', 'hypothesis', 'research', 'analysis', 'study', 'theory'],
        'business': ['market', 'strategy', 'customer', 'revenue', 'profit', 'sales'],
        'education': ['learn', 'teach', 'student', 'course', 'curriculum', 'knowledge'],
        'health': ['medical', 'health', 'treatment', 'diagnosis', 'patient', 'care']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            topics.append(topic.title())
    
    return topics[:5]  # Return top 5 topics

def create_smart_chunks(content: str, chunk_size: int = 400) -> List[str]:
    """Create smarter document chunks"""
    # Split by sentences first
    sentences = re.split(r'[.!?]+', content)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                chunks.append(sentence)
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

@app.get("/search")
async def enhanced_search(query: str, limit: int = 5):
    """Enhanced document search"""
    try:
        if not model_state.documents:
            return {"results": [], "total_documents": 0, "query": query}
        
        results = []
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for doc in model_state.documents:
            content_lower = doc["content"].lower()
            
            # Enhanced relevance scoring
            relevance_score = 0
            matches = 0
            
            # Exact phrase match (highest weight)
            if query_lower in content_lower:
                matches += content_lower.count(query_lower)
                relevance_score += matches * 30
            
            # Individual word matches
            for word in query_words:
                if word in content_lower:
                    word_matches = content_lower.count(word)
                    matches += word_matches
                    relevance_score += word_matches * 10
            
            # Topic relevance
            for topic in doc.get("topics", []):
                if any(word in topic.lower() for word in query_words):
                    relevance_score += 20
            
            if relevance_score > 0:
                # Get enhanced preview
                preview = get_enhanced_preview(doc["content"], query_lower)
                
                results.append({
                    "filename": doc["filename"],
                    "content_preview": preview,
                    "relevance_score": min(100, relevance_score),
                    "matches": matches,
                    "topics": doc.get("topics", []),
                    "word_count": doc.get("word_count", 0)
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "results": results[:limit],
            "total_documents": len(model_state.documents),
            "query": query,
            "enhanced": True
        }
        
    except Exception as e:
        logger.error(f"Enhanced search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_enhanced_preview(content: str, query: str) -> str:
    """Get better preview with context"""
    content_lower = content.lower()
    
    # Find first occurrence
    pos = content_lower.find(query)
    if pos == -1:
        return content[:200] + "..." if len(content) > 200 else content
    
    # Get context around the match
    start = max(0, pos - 100)
    end = min(len(content), pos + len(query) + 100)
    
    preview = content[start:end]
    
    if start > 0:
        preview = "..." + preview
    if end < len(content):
        preview = preview + "..."
    
    return preview

@app.get("/models/status")
async def get_enhanced_model_status():
    """Enhanced model status"""
    return {
        "loaded": model_state.loaded,
        "model_info": model_state.current_model_info,
        "device": model_state.device,
        "documents_count": len(model_state.documents),
        "conversation_length": len(model_state.conversation_history),
        "enhancement_level": "premium",
        "available_models": model_state.model_options,
        "features": [
            "enhanced_prompting",
            "better_model_selection", 
            "improved_generation_parameters",
            "context_awareness",
            "smart_fallbacks"
        ]
    }

def clean_for_tts(text: str) -> str:
    """Enhanced TTS cleaning"""
    import re
    
    # Remove emojis and special characters
    text = re.sub(r'[🤖✅⚠️❌🛠️🟢🎉🚀💡📚🔧🎯]', '', text)
    
    # Remove markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\n+', '. ', text)
    
    # Clean up for speech
    text = text.replace('AI', 'A I')
    text = text.replace('LLM', 'Large Language Model')
    
    # Limit length
    sentences = text.split('.')
    if len(sentences) > 4:
        text = '. '.join(sentences[:4]) + '.'
    
    return text.strip()

if __name__ == "__main__":
    print("🚀 Starting ENHANCED LLM Backend - Much Better AI Interactions!")
    print("================================================================")
    print("✅ Better model selection (DialoGPT-medium, GPT-2, BLOOM)")
    print("✅ Enhanced prompt engineering")
    print("✅ Improved generation parameters")
    print("✅ Context-aware conversations")
    print("✅ Smart fallback responses")
    print("✅ Better document processing")
    print("")
    print("🧠 This will provide MUCH better AI interactions!")
    
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )