from typing import List, Dict, Optional, Any
from loguru import logger
from app.config import settings
from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.model_registry import get_model_for_mode

class LLMService:
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {
            "openrouter": OpenRouterProvider(),
            "groq": GroqProvider()
        }
        self.primary_provider = settings.llm_primary_provider
        self.fallback_provider = settings.llm_fallback_provider

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        mode: str = "assistant",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generates a response using the primary provider, with fallback to secondary if needed.
        """
        provider_name = self.primary_provider
        
        try:
            return await self._call_provider(
                provider_name, messages, mode, temperature, max_tokens, **kwargs
            )
        except Exception as e:
            logger.warning(f"Primary provider {provider_name} failed: {str(e)}. Attempting fallback...")
            
            if self.fallback_provider and self.fallback_provider != provider_name:
                try:
                    fallback_response = await self._call_provider(
                        self.fallback_provider, messages, mode, temperature, max_tokens, **kwargs
                    )
                    logger.info(f"Fallback to {self.fallback_provider} successful.")
                    return fallback_response
                except Exception as fe:
                    logger.error(f"Fallback provider {self.fallback_provider} also failed: {str(fe)}")
                    raise Exception(f"Both primary and fallback LLM providers failed. Last error: {str(fe)}")
            else:
                raise e

    async def _call_provider(
        self,
        provider_name: str,
        messages: List[Dict[str, str]],
        mode: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")

        model = get_model_for_mode(provider_name, mode)
        logger.info(f"Calling LLM: provider={provider_name}, model={model}, mode={mode}")
        
        return await provider.generate_response(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

llm_service = LLMService()
