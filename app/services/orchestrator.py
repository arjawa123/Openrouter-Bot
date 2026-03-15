import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db import crud
from app.db.models import User
from app.services.openrouter_client import openrouter_client
from app.services.memory_service import get_memories_context
from app.utils.urls import extract_urls
from app.services.scraper_service import fetch_and_extract_content

def load_prompt(mode: str) -> str:
    filepath = os.path.join("app", "prompts", f"{mode}.txt")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a helpful AI assistant."

async def process_chat_message(
    db: AsyncSession, 
    user: User, 
    chat_id: int, 
    user_input: str,
    mode_override: str = None
) -> str:
    # 1. Determine mode and model
    mode = mode_override or user.default_mode
    model = user.default_model or settings.openrouter_model_default
    
    if mode == 'coder':
        model = settings.openrouter_model_code
    elif mode == 'researcher':
        model = settings.openrouter_model_research

    # 2. Check for URLs if in researcher mode or generally
    urls = extract_urls(user_input)
    scraped_context = ""
    if urls:
        extracted = await fetch_and_extract_content(urls[0]) # just do first URL for now
        if not extracted.startswith("Error"):
            scraped_context = f"\n\nContent from URL ({urls[0]}):\n{extracted}"
            if not mode_override:
                mode = 'researcher' # Auto-switch to researcher if URL is sent

    # 3. Get system prompt template
    sys_prompt_template = load_prompt(mode)
    
    # 4. Get Memory Context
    memory_context = await get_memories_context(db, user.id)
    
    # 5. Build full context
    full_context = ""
    if memory_context:
        full_context += memory_context + "\n"
    if scraped_context:
        full_context += scraped_context
        
    # 6. Format system prompt
    system_prompt = sys_prompt_template.format(
        language=user.language,
        preferred_name=user.preferred_name or user.first_name,
        style=user.style,
        context=full_context
    )

    # 7. Get conversation history
    conv = await crud.get_or_create_conversation(db, user.id, chat_id)
    recent_msgs = await crud.get_recent_messages(db, conv.id, limit=6)
    
    # 8. Build OpenRouter messages payload
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent_msgs:
        messages.append({"role": msg.role, "content": msg.content})
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})

    # 9. Call OpenRouter
    ai_response = await openrouter_client.chat_completion(
        messages=messages,
        model=model
    )

    # 10. Save to DB
    await crud.create_message(db, conv.id, role="user", content=user_input)
    await crud.create_message(db, conv.id, role="assistant", content=ai_response)

    return ai_response
