import os
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.db import crud
from app.db.models import User
from app.services.llm.llm_service import llm_service
from app.services.memory_service import get_memories_context
from app.utils.urls import extract_urls
from app.services.scraper_service import fetch_and_extract_content
from app.services.memory_intelligence import memory_intelligence
from app.services.intent_service import intent_service, Intent

class AssistantService:
    def _load_prompt(self, mode: str) -> str:
        filepath = os.path.join("app", "prompts", f"{mode}.txt")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return "You are a helpful AI assistant."

    async def get_system_prompt(self, db: AsyncSession, user: User, mode: str, additional_context: str = "") -> str:
        """
        Builds the complete system prompt with user profile, memory, and any extra context.
        """
        template = self._load_prompt(mode)
        
        # Get Memory Context (Long-term)
        memory_context = await get_memories_context(db, user.id)
        
        # Combine contexts
        full_context = ""
        if memory_context:
            full_context += f"RELEVANT MEMORIES:\n{memory_context}\n"
        if additional_context:
            full_context += f"ADDITIONAL CONTEXT:\n{additional_context}\n"

        # Format template
        try:
            return template.format(
                language=getattr(user, 'language', 'English') or "English",
                preferred_name=getattr(user, 'preferred_name', None) or user.first_name,
                style=getattr(user, 'style', 'helpful and professional') or "helpful and professional",
                context=full_context
            )
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            return template

    async def chat(
        self, 
        db: AsyncSession, 
        user: User, 
        chat_id: int, 
        user_input: str,
        mode_override: str = None,
        additional_context: str = ""
    ) -> str:
        """
        Main chat interaction entry point.
        """
        mode = mode_override or user.default_mode
        
        # 1. Scrape URLs if present
        urls = extract_urls(user_input)
        scraped_context = ""
        if urls:
            extracted = await fetch_and_extract_content(urls[0])
            if not extracted.startswith("Error"):
                scraped_context = f"Content from URL ({urls[0]}):\n{extracted}"
                if not mode_override:
                    mode = 'researcher'

        # 2. Prepare System Prompt
        # Combine scraped info with any context from the orchestrator (e.g., action confirmations)
        combined_context = additional_context
        if scraped_context:
            combined_context += "\n" + scraped_context

        system_prompt = await self.get_system_prompt(db, user, mode, combined_context)

        # 3. Build message history
        conv = await crud.get_or_create_conversation(db, user.id, chat_id)
        recent_msgs = await crud.get_recent_messages(db, conv.id, limit=8)
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_msgs:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_input})

        # 4. Call LLM Service (with fallback)
        try:
            llm_response = await llm_service.generate_response(
                messages=messages,
                mode=mode
            )
            ai_content = llm_response.content
            
            # 5. Persist interaction
            await crud.create_message(db, conv.id, role="user", content=user_input)
            await crud.create_message(db, conv.id, role="assistant", content=ai_content)
            
            # 6. Post-processing: Fact Extraction (Background task)
            # We await this for reliability in this version, but can be a background task if needed.
            await memory_intelligence.extract_and_save_facts(db, user.id, user_input, ai_content)
            
            return ai_content
        except Exception as e:
            logger.error(f"Assistant chat failed: {str(e)}")
            return "I'm sorry, I'm having trouble thinking right now. Please try again later."

assistant_service = AssistantService()
