from typing import Dict, Any
from app.config import settings

# Mapping of assistant modes to provider-specific models
MODEL_REGISTRY = {
    "openrouter": {
        "assistant": settings.openrouter_model_default,
        "coder": settings.openrouter_model_code,
        "planner": settings.openrouter_model_default,
        "researcher": settings.openrouter_model_research,
    },
    "groq": {
        "assistant": "llama-3.3-70b-versatile",
        "coder": "llama-3.3-70b-versatile",
        "planner": "llama-3.3-70b-versatile",
        "researcher": "llama-3.3-70b-versatile",
    }
}

def get_model_for_mode(provider_name: str, mode: str) -> str:
    """Get the appropriate model for a given provider and assistant mode."""
    provider_models = MODEL_REGISTRY.get(provider_name, MODEL_REGISTRY["openrouter"])
    return provider_models.get(mode, provider_models.get("assistant"))
