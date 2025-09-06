import json
import pickle
import hashlib
from typing import Any, Optional, Union, Dict
import redis.asyncio as redis
import logging
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=False)
            await self.client.ping()
            logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("🔒 Redis cache disconnected")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        if not self.client:
            return False
        
        try:
            # Try to serialize as JSON first, then pickle
            try:
                serialized = json.dumps(value, default=str)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)
            
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern"""
        if not self.client:
            return 0
        
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

# Global cache instance
cache = RedisCache()

def cached(prefix: str = "default", ttl: int = 3600, skip_cache: bool = False):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if skip_cache or not cache.client:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache._generate_key(prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

class CacheManager:
    """Manager class for cache operations"""
    
    @staticmethod
    async def clear_user_cache(user_id: str):
        """Clear all cache entries for a specific user"""
        pattern = f"*user:{user_id}*"
        cleared = await cache.clear_pattern(pattern)
        logger.info(f"Cleared {cleared} cache entries for user {user_id}")
        return cleared
    
    @staticmethod
    async def clear_model_cache(model_name: str):
        """Clear all cache entries for a specific model"""
        pattern = f"*model:{model_name}*"
        cleared = await cache.clear_pattern(pattern)
        logger.info(f"Cleared {cleared} cache entries for model {model_name}")
        return cleared
    
    @staticmethod
    async def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        if not cache.client:
            return {"status": "disconnected"}
        
        try:
            info = await cache.client.info()
            return {
                "status": "connected",
                "memory_used": info.get("used_memory_human", "N/A"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "uptime": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}
