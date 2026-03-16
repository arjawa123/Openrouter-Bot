from typing import List
from loguru import logger
from app.services.llm.llm_service import llm_service
from app.db import crud
from sqlalchemy.ext.asyncio import AsyncSession

class MemoryIntelligenceService:
    async def extract_and_save_facts(self, db: AsyncSession, user_id: int, user_input: str, assistant_output: str):
        """
        Analyze a conversation turn to extract facts for long-term memory.
        """
        system_prompt = """
        You are a memory specialist for an AI assistant.
        Identify important facts about the user from this conversation.
        Only extract stable facts (preferences, job, location, family, habits, goals).
        Format: Return only the facts, one per line. No bullets. No intro.
        If no new facts are found, reply ONLY with "NONE".
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User: {user_input}\nAssistant: {assistant_output}"}
        ]

        try:
            # Low temperature for extraction accuracy
            response = await llm_service.generate_response(
                messages=messages,
                temperature=0,
                max_tokens=150
            )
            
            content = response.content.strip()
            if not content or content.upper() == "NONE":
                return

            facts = [f.strip() for f in content.split("\n") if f.strip() and len(f.strip()) > 5]
            for fact in facts:
                await crud.create_memory(db, user_id, content=fact)
                logger.info(f"Auto-extracted memory for user {user_id}: {fact}")

        except Exception as e:
            logger.error(f"Fact extraction failed: {str(e)}")

memory_intelligence = MemoryIntelligenceService()
