from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.db import crud
from app.services.llm.llm_service import llm_service
from loguru import logger

class DigestService:
    async def generate_digest(self, db: AsyncSession, user: User) -> str:
        """Generate a narrative and personalized daily digest for the user using LLM."""
        
        # 1. Gather all relevant data
        todos = await crud.get_pending_todos(db, user.id)
        notes = await crud.get_notes(db, user.id, limit=5)
        memories = await crud.get_user_memories(db, user.id, limit=10)
        
        todos_str = "\n".join([f"- {t.text} (Due: {t.due_at})" for t in todos]) or "No pending tasks."
        notes_str = "\n".join([f"- {n.content}" for n in notes]) or "No recent notes."
        memories_str = "\n".join([f"- {m.content}" for m in memories]) or "No significant memories yet."
        
        # 2. Construct LLM Prompt
        system_prompt = f"""
        You are a high-end personal executive assistant.
        Your task is to write a warm, professional, and encouraging daily digest for the user.
        
        Use the provided data to:
        1. Greet them by their preferred name: {user.preferred_name or user.first_name}.
        2. Summarize their pending tasks and highlight anything due soon.
        3. Briefly mention recent notes if relevant.
        4. Use the "Memories" to personalize the tone (e.g., if you know they like coffee, mention it).
        
        Style: {user.style or "professional yet friendly"}.
        Language: {user.language or "English"}.
        Format: Use Markdown for Telegram. Keep it concise but helpful.
        """
        
        user_context = f"""
        PENDING TODOS:
        {todos_str}
        
        RECENT NOTES:
        {notes_str}
        
        WHAT I REMEMBER ABOUT YOU:
        {memories_str}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please generate my daily digest based on this info:\n{user_context}"}
        ]

        try:
            response = await llm_service.generate_response(
                messages=messages,
                mode="assistant"
            )
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate narrative digest: {e}")
            # Fallback to a simpler version
            return f"🌅 *Daily Digest for {user.preferred_name or user.first_name}*\n\nTasks:\n{todos_str}\n\nNotes:\n{notes_str}"

digest_service = DigestService()
