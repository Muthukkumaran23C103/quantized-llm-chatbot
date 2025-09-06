import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional, Any
import ollama
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[str] = None

class ModelConfig(BaseModel):
    name: str
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 2048
    stop: Optional[List[str]] = None

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.client = ollama.Client(host=host)
        self.async_client = httpx.AsyncClient(timeout=30.0)
        
    async def health_check(self) -> bool:
        try:
            response = await self.async_client.get(f"{self.host}/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            response = await self.async_client.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        try:
            response = await self.async_client.post(
                f"{self.host}/api/pull",
                json={"name": model_name},
                timeout=300.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def generate_sync(
        self, 
        model: str, 
        prompt: str, 
        config: Optional[ModelConfig] = None
    ) -> str:
        try:
            if config is None:
                config = ModelConfig(name=model)
            
            response = self.client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': config.temperature,
                    'top_p': config.top_p,
                    'top_k': config.top_k,
                    'num_predict': config.max_tokens,
                    'stop': config.stop or []
                },
                stream=False
            )
            return response.get('response', '')
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error: {str(e)}"
    
    async def generate_stream(
        self,
        model: str,
        prompt: str,
        config: Optional[ModelConfig] = None
    ) -> AsyncGenerator[str, None]:
        if config is None:
            config = ModelConfig(name=model)
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    'temperature': config.temperature,
                    'top_p': config.top_p,
                    'top_k': config.top_k,
                    'num_predict': config.max_tokens,
                    'stop': config.stop or []
                }
            }
            
            async with self.async_client.stream(
                "POST", 
                f"{self.host}/api/generate",
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    yield f"Error: HTTP {response.status_code}"
                    return
                
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            if 'response' in data:
                                yield data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield f"Error: {str(e)}"
    
    async def chat_stream(
        self,
        model: str,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None
    ) -> AsyncGenerator[str, None]:
        if config is None:
            config = ModelConfig(name=model)
        
        try:
            ollama_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            payload = {
                "model": model,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    'temperature': config.temperature,
                    'top_p': config.top_p,
                    'top_k': config.top_k,
                    'num_predict': config.max_tokens,
                }
            }
            
            async with self.async_client.stream(
                "POST",
                f"{self.host}/api/chat", 
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    yield f"Error: HTTP {response.status_code}"
                    return
                
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            if 'message' in data and 'content' in data['message']:
                                yield data['message']['content']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Streaming chat failed: {e}")
            yield f"Error: {str(e)}"
    
    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None
    ) -> str:
        if config is None:
            config = ModelConfig(name=model)
        
        try:
            ollama_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            payload = {
                "model": model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    'temperature': config.temperature,
                    'top_p': config.top_p,
                    'top_k': config.top_k,
                    'num_predict': config.max_tokens,
                }
            }
            
            response = await self.async_client.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return f"Error: {str(e)}"

    async def close(self):
        await self.async_client.aclose()
