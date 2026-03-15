import httpx
from loguru import logger
from typing import List, Dict, Any, Optional
from app.config import settings

class OpenRouterClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = settings.openrouter_api_key.get_secret_value()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
            "Content-Type": "application/json"
        }

    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        target_model = model or settings.openrouter_model_default
        
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Unexpected OpenRouter response format: {data}")
                    return "Sorry, I received an unexpected response from the AI."
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred calling OpenRouter: {e.response.text}")
            return "Sorry, I encountered an error communicating with the AI service."
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {str(e)}")
            return "Sorry, an unexpected error occurred while processing your request."

openrouter_client = OpenRouterClient()
