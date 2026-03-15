from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.services import todo_service, notes_service

async def generate_digest(db: AsyncSession, user: User) -> str:
    """Generate a daily digest for the user."""
    
    digest = f"🌅 *Daily Digest for {user.preferred_name or user.first_name}* 🌅\n\n"
    
    # Profile info
    digest += f"Current Mode: `{user.default_mode}`\n"
    
    # Todos
    todos = await todo_service.list_todos(db, user.id)
    digest += f"\n📝 *Todos*\n{todos}\n"
    
    # Notes
    notes = await notes_service.list_notes(db, user.id)
    digest += f"\n📓 *Recent Notes*\n{notes}"
    
    return digest
