from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud

class NotesService:
    async def add_note(self, db: AsyncSession, user_id: int, content: str) -> str:
        await crud.create_note(db, user_id, content)
        return "Note saved successfully."

    async def list_notes(self, db: AsyncSession, user_id: int) -> str:
        notes = await crud.get_notes(db, user_id, limit=10)
        if not notes:
            return "You have no notes."
            
        res = "Your recent notes:\n"
        for i, n in enumerate(notes, 1):
            res += f"{i}. {n.content[:50]}...\n"
        return res

notes_service = NotesService()
