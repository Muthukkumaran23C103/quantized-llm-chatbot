import time
from typing import Dict, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
    
    async def connect(self):
        """Initialize Redis connection for rate limiting"""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("✅ Rate limiter Redis connected")
        except Exception as e:
            logger.error(f"❌ Rate limiter Redis connection failed: {e}")
    
    async def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed based on rate limit
        Uses sliding window algorithm
        """
        if not self.client:
            # If Redis is not available, allow the request
            return True, {"remaining": limit, "reset": time.time() + window}
        
        try:
            current_time = time.time()
            pipeline = self.client.pipeline()
            
            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, current_time - window)
            
            # Count current requests
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})
            
            # Set expiration for the key
            pipeline.expire(key, window)
            
            results = await pipeline.execute()
            current_requests = results[1]
            
            if current_requests < limit:
                remaining = limit - current_requests - 1
                reset = current_time + window
                return True, {"remaining": remaining, "reset": reset}
            else:
                # Find when the oldest request will expire
                oldest = await self.client.zrange(key, 0, 0, withscores=True)
                reset = oldest[0][1] + window if oldest else current_time + window
                return False, {"remaining": 0, "reset": reset}
                
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # In case of Redis errors, allow the request
            return True, {"remaining": limit, "reset": time.time() + window}

# Global rate limiter instance
rate_limiter = RateLimiter()

class RateLimitMiddleware:
    def __init__(
        self,
        calls: int = 100,
        period: int = 60,
        key_func: Callable[[Request], str] = None
    ):
        self.calls = calls
        self.period = period
        self.key_func = key_func or self._default_key_func
    
    def _default_key_func(self, request: Request) -> str:
        """Default key function using client IP"""
        client_ip = request.client.host
        return f"rate_limit:{client_ip}"
    
    async def __call__(self, request: Request, call_next):
        # Generate rate limit key
        key = self.key_func(request)
        
        # Check rate limit
        allowed, info = await rate_limiter.is_allowed(key, self.calls, self.period)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.calls} requests per {self.period} seconds",
                    "retry_after": int(info["reset"] - time.time())
                },
                headers={
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(int(info["reset"])),
                    "Retry-After": str(int(info["reset"] - time.time()))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(info["reset"]))
        
        return response

def user_rate_limit_key(request: Request) -> str:
    """Rate limit key based on authenticated user"""
    # Try to extract user from token
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # You'd decode the token here to get user ID
        token = auth_header[7:]
        return f"rate_limit:user:{token[:10]}"  # Use part of token as key
    
    # Fallback to IP-based rate limiting
    return f"rate_limit:ip:{request.client.host}"

def endpoint_rate_limit_key(request: Request) -> str:
    """Rate limit key based on endpoint"""
    path = request.url.path
    client_ip = request.client.host
    return f"rate_limit:endpoint:{path}:{client_ip}"
