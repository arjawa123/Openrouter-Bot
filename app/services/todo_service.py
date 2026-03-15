from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud

async def add_todo(db: AsyncSession, user_id: int, text: str) -> str:
    await crud.create_todo(db, user_id, text)
    return f"Todo added: {text}"

async def list_todos(db: AsyncSession, user_id: int) -> str:
    todos = await crud.get_pending_todos(db, user_id)
    if not todos:
        return "You have no pending todos."
    
    res = "Your pending todos:\n"
    for t in todos:
        res += f"{t.id}. {t.text}\n"
    return res

async def mark_done(db: AsyncSession, user_id: int, todo_id: int) -> str:
    success = await crud.mark_todo_done(db, user_id, todo_id)
    if success:
        return f"Todo #{todo_id} marked as done."
    return f"Todo #{todo_id} not found."
