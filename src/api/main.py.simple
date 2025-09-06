import asyncio
import os
import yaml
import time
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import structlog

# Import Phase 4 modules
from src.auth.auth import auth_manager, get_current_user, require_admin_role, UserLogin, TokenResponse
from src.cache.redis_cache import cache, cached, CacheManager
from src.middleware.rate_limit import rate_limiter, RateLimitMiddleware, user_rate_limit_key
### #, get_prometheus_metrics

# Import existing modules
from src.database.vector_db import EnhancedVectorDatabase, SearchResult
from src.inference.ollama.client import OllamaClient, ChatMessage, ModelConfig
from src.nlp.processor import NLPProcessor, ProcessedText
# Add these imports to your existing main.py
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os



# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if os.getenv("ENVIRONMENT") == "production" else structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Load model configuration
with open('config/models.yml', 'r') as f:
    config = yaml.safe_load(f)

# Global variables
ollama_client = None
db = None
nlp_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global ollama_client, db, nlp_processor
    
    logger.info("🚀 Starting Phase 4: Production-Ready LLM Chatbot...")
    
    # Initialize Redis cache
    await cache.connect()
    await rate_limiter.connect()
    
    # Initialize NLP processor with caching
    try:
        nlp_processor = NLPProcessor()
        logger.info("✅ NLP processor initialized")
    except Exception as e:
        logger.error("❌ Failed to initialize NLP processor", error=str(e))
        raise
    
    # Initialize enhanced database
    try:
        db = EnhancedVectorDatabase(db_path=os.getenv("DATABASE_PATH", "data/chatbot.db"))
        logger.info("✅ Enhanced vector database initialized")
    except Exception as e:
        logger.error("❌ Failed to initialize database", error=str(e))
        raise
    
    # Initialize Ollama client
    try:
        ollama_client = OllamaClient()
        
        if not await ollama_client.health_check():
            logger.warning("⚠️  Ollama server not responding")
        else:
            models = await ollama_client.list_models()
            logger.info("✅ Ollama ready", model_count=len(models))
    except Exception as e:
        logger.error("❌ Failed to initialize Ollama client", error=str(e))
        raise
    
    yield
    
    # Shutdown
    if ollama_client:
        await ollama_client.close()
    if db:
        db.close()
    await cache.disconnect()
    logger.info("🔒 Resources cleaned up")

# Create FastAPI app with production features
app = FastAPI(
    title="Production LLM Chatbot with Authentication & Caching",
    description="Phase 4: Production-ready system with auth, caching, rate limiting, and monitoring",
    version="0.4.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

app.mount("/static", StaticFiles(directory="src/frontend"), name="static")

@app.get("/ui", response_class=HTMLResponse)
async def web_interface():
    """Serve the modern web interface for students"""
    with open("src/frontend/web_ui.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/gradio")
async def gradio_interface():
    """Redirect to Gradio interface"""
    return {"message": "Gradio interface available at port 7860", "url": "http://localhost:7860"}

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
# # app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware with different limits per endpoint
general_rate_limit = RateLimitMiddleware(calls=100, period=60)
api_rate_limit = RateLimitMiddleware(calls=50, period=60, key_func=user_rate_limit_key)

# Pydantic models for Phase 4
class HealthResponse(BaseModel):
    status: str
    version: str
    components: dict
    uptime_seconds: float
    cache_stats: dict

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    processing_time_ms: int
    analysis: dict
    cached: bool = False

class CachedChatResponse(BaseModel):
    user_message: str
    bot_response: str
    model_used: str
    session_id: Optional[str] = None
    response_time_ms: int
    context_documents: List[dict] = []
    processed_query: dict = {}
    from_cache: bool = False

# Helper functions
async def ensure_model_available(model_name: str) -> bool:
    """Ensure model is available with caching"""
    cache_key = f"model_available:{model_name}"
    
    # Check cache first
    is_available = await cache.get(cache_key)
    if is_available is not None:
        return is_available
    
    # Check actual availability
    models = await ollama_client.list_models()
    available_models = [m['name'] for m in models]
    available = model_name in available_models
    
    if not available:
        logger.info("📥 Downloading model", model=model_name)
        success = await ollama_client.pull_model(model_name)
        available = success
        if success:
            logger.info("✅ Model downloaded", model=model_name)
    
    # Cache result for 1 hour
    await cache.set(cache_key, available, ttl=3600)
    return available

# Authentication routes
@app.post("/auth/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """Authenticate user and return JWT tokens"""
    start_time = time.time()
    
    try:
        user = auth_manager.authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
##            ##metrics.record_cache_operation("auth", "failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create tokens
        access_token = auth_manager.create_access_token(data={"sub": user["username"], "role": user["role"]})
        refresh_token = auth_manager.create_refresh_token(data={"sub": user["username"]})
        
##        ##metrics.record_cache_operation("auth", "success")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(status_code=500, detail="Authentication service error")

# Enhanced API Routes
@app.get("/", dependencies=[Depends(general_rate_limit)])
async def root():
    return {
        "message": "Production LLM Chatbot - Phase 4",
        "status": "running",
        "version": "0.4.0",
        "phase": "Production Enhancement",
        "features": [
            "JWT Authentication",
            "Redis Caching",
            "Rate Limiting",
            "Monitoring & Metrics",
            "Role-based Access Control",
            "Production Security"
        ]
    }

@app.get("/health", response_model=HealthResponse, dependencies=[Depends(general_rate_limit)])
async def enhanced_health_check():
    start_time = time.time()
    
    try:
        # Check all system components
        db_stats = db.get_database_stats()
        ollama_healthy = await ollama_client.health_check()
        cache_stats = await CacheManager.get_cache_stats()
##        app_info = ##metrics.get_application_info()
        
        return HealthResponse(
            status="healthy" if ollama_healthy else "partial",
            version="0.4.0",
            components={
                "database": "connected",
                "ollama": "connected" if ollama_healthy else "disconnected",
                "nlp_processor": "loaded",
                "redis_cache": cache_stats["status"],
                "rate_limiter": "active"
            },
            uptime_seconds=app_info["uptime_seconds"],
            cache_stats=cache_stats
        )
    except Exception as e:
        logger.error("Health check error", error=str(e))
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

# Admin routes
@app.get("/admin/stats")
async def admin_stats(admin_user = Depends(require_admin_role)):
    """Get comprehensive system statistics (admin only)"""
    try:
        db_stats = db.get_database_stats()
        cache_stats = await CacheManager.get_cache_stats()
##        app_info = ##metrics.get_application_info()
        
        return {
            "database": db_stats,
            "cache": cache_stats,
            "system": app_info,
            "models": await ollama_client.list_models()
        }
    except Exception as e:
        logger.error("Admin stats error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/cache/clear")
async def clear_cache(admin_user = Depends(require_admin_role)):
    """Clear entire cache (admin only)"""
    try:
        cleared = await cache.clear_pattern("*")
        logger.info("Cache cleared by admin", cleared_keys=cleared, admin=admin_user.username)
        return {"status": "success", "cleared_keys": cleared}
    except Exception as e:
        logger.error("Cache clear error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Metrics endpoint for Prometheus
##@app.get("/metrics", response_class=PlainTextResponse)
##async def prometheus_metrics():
##    """Prometheus metrics endpoint"""
##    return get_prometheus_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        log_config=None  # Use our custom logging
    )

# Add this to your main.py after the existing endpoints

class ChatMessage(BaseModel):
    message: str
    use_context: bool = True
    max_context_docs: int = 3

class ChatResponse(BaseModel):
    bot_response: str
    response_time_ms: int = 0

@app.post("/search")  
async def semantic_search():
    """Search endpoint placeholder"""
    return {"message": "🔍 Semantic search feature coming soon!"}


@app.post("/chat")
async def chat_endpoint(request: dict):
    """Student-friendly chat endpoint"""
    message = request.get("message", "")
    
    response = f"🤖 **AI Study Buddy says:**\n\n"
    response += f"I heard you say: *'{message}'* 📝\n\n"
    response += "📚 **Study Help Available:**\n"
    response += "• Ask me about any subject\n"
    response += "• Upload your notes for personalized help\n"
    response += "• Search through your study materials\n\n"
    response += "💡 **Study Tip:** Try explaining concepts out loud - it helps retention!\n\n"
    response += "🎯 This is a demo response. Full AI features coming soon!"
    
    return {
        "bot_response": response,
        "response_time_ms": 100,
        "context_documents": [],
        "metadata": {"status": "demo_mode"}
    }

@app.post("/documents")
async def upload_document(request: dict):
    """Document upload endpoint"""
    return {
        "message": "📁 Document upload feature - coming soon!",
        "analysis": {"word_count": 0, "keywords": []},
        "processing_time_ms": 50
    }
