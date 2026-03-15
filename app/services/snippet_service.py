from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud

async def save_snippet(db: AsyncSession, user_id: int, name: str, content: str) -> str:
    await crud.create_snippet(db, user_id, name, content)
    return f"Snippet '{name}' saved successfully."

async def get_snippet(db: AsyncSession, user_id: int, name: str) -> str:
    snippet = await crud.get_snippet(db, user_id, name)
    if not snippet:
        return f"Snippet '{name}' not found."
    
    # Return formatted markdown
    lang = snippet.language or ""
    return f"Snippet: {name}\n```{lang}\n{snippet.content}\n```"
