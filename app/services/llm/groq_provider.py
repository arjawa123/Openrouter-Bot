import httpx
from loguru import logger
from typing import List, Dict, Optional, Any
from app.config import settings
from app.services.llm.base import BaseLLMProvider, LLMResponse

class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = "https://api.groq.com/openai/v1"
        self.api_key = settings.groq_api_key.get_secret_value() if settings.groq_api_key else None
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @property
    def name(self) -> str:
        return "groq"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        if not self.api_key:
            raise Exception("Groq API key not configured")

        url = f"{self.base_url}/chat/completions"
        target_model = model or settings.groq_model_default
        
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        payload.update(kwargs)

        try:
            async with httpx.AsyncClient(timeout=float(settings.llm_request_timeout)) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content") or ""
                    usage = data.get("usage")
                    return LLMResponse(
                        content=content,
                        provider=self.name,
                        model=target_model,
                        usage=usage,
                        raw_response=data
                    )
                else:
                    raise Exception(f"Unexpected response format: {data}")
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq HTTP Error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Groq Error: {str(e)}")
            raise
