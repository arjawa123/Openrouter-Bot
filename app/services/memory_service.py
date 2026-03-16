from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud

class MemoryService:
    async def remember(self, db: AsyncSession, user_id: int, content: str) -> str:
        """Save a memory explicitly."""
        await crud.create_memory(db, user_id, content)
        return f"I will remember this: {content}"

    async def forget(self, db: AsyncSession, user_id: int, keyword: str) -> str:
        """Forget a memory by keyword."""
        count = await crud.delete_memory_by_keyword(db, user_id, keyword)
        if count > 0:
            return f"I have forgotten {count} memory(ies) containing '{keyword}'."
        return f"I couldn't find any memories containing '{keyword}'."

    async def get_memories_context(self, db: AsyncSession, user_id: int) -> str:
        """Get recent memories to inject into prompt context."""
        memories = await crud.get_user_memories(db, user_id, limit=5)
        if not memories:
            return ""
            
        context = "User's recent memories:\n"
        for m in memories:
            context += f"- {m.content}\n"
        return context

# Instantiate for use as an object
memory_service = MemoryService()

# Maintain standalone function compatibility for get_memories_context if needed
async def get_memories_context(db: AsyncSession, user_id: int) -> str:
    return await memory_service.get_memories_context(db, user_id)
