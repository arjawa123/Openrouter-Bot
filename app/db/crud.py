from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import Optional, List, Dict, Any
from app.db.models import User, Conversation, Message, Memory, Note, Todo, Snippet, ScrapedPageCache
from datetime import datetime, timezone

# --- User ---
async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.telegram_user_id == telegram_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, telegram_id: int, username: str = None, first_name: str = None) -> User:
    user = User(telegram_user_id=telegram_id, username=username, first_name=first_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user_id: int, data: Dict[str, Any]) -> User:
    stmt = update(User).where(User.id == user_id).values(**data).returning(User)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()

# --- Conversation & Messages ---
async def get_or_create_conversation(db: AsyncSession, user_id: int, chat_id: int) -> Conversation:
    result = await db.execute(select(Conversation).where(
        Conversation.user_id == user_id, 
        Conversation.chat_id == chat_id
    ))
    conv = result.scalar_one_or_none()
    if not conv:
        conv = Conversation(user_id=user_id, chat_id=chat_id)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
    return conv

async def get_recent_messages(db: AsyncSession, conversation_id: int, limit: int = 10) -> List[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())[::-1] # Reverse to get chronological order

async def create_message(db: AsyncSession, conversation_id: int, role: str, content: str) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    
    # Update conversation last_message_at
    await db.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(last_message_at=datetime.now(timezone.utc))
    )
    
    await db.commit()
    return msg

# --- Memories ---
async def get_user_memories(db: AsyncSession, user_id: int, limit: int = 5) -> List[Memory]:
    result = await db.execute(
        select(Memory)
        .where(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

async def create_memory(db: AsyncSession, user_id: int, content: str) -> Memory:
    memory = Memory(user_id=user_id, content=content)
    db.add(memory)
    await db.commit()
    return memory

async def delete_memory_by_keyword(db: AsyncSession, user_id: int, keyword: str) -> int:
    stmt = delete(Memory).where(
        Memory.user_id == user_id,
        Memory.content.ilike(f"%{keyword}%")
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount

# --- Todos ---
async def create_todo(db: AsyncSession, user_id: int, text: str) -> Todo:
    todo = Todo(user_id=user_id, text=text)
    db.add(todo)
    await db.commit()
    return todo

async def get_pending_todos(db: AsyncSession, user_id: int) -> List[Todo]:
    result = await db.execute(
        select(Todo)
        .where(Todo.user_id == user_id, Todo.status == "pending")
        .order_by(Todo.created_at.asc())
    )
    return list(result.scalars().all())

async def mark_todo_done(db: AsyncSession, user_id: int, todo_id: int) -> bool:
    stmt = update(Todo).where(
        Todo.user_id == user_id, Todo.id == todo_id
    ).values(status="done")
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# --- Notes ---
async def create_note(db: AsyncSession, user_id: int, content: str) -> Note:
    note = Note(user_id=user_id, content=content)
    db.add(note)
    await db.commit()
    return note

async def get_notes(db: AsyncSession, user_id: int, limit: int = 5) -> List[Note]:
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user_id)
        .order_by(Note.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

# --- Snippets ---
async def create_snippet(db: AsyncSession, user_id: int, name: str, content: str, language: str = None) -> Snippet:
    # Delete if exists
    await db.execute(delete(Snippet).where(Snippet.user_id == user_id, Snippet.name == name))
    
    snippet = Snippet(user_id=user_id, name=name, content=content, language=language)
    db.add(snippet)
    await db.commit()
    return snippet

async def get_snippet(db: AsyncSession, user_id: int, name: str) -> Optional[Snippet]:
    result = await db.execute(
        select(Snippet).where(Snippet.user_id == user_id, Snippet.name == name)
    )
    return result.scalar_one_or_none()
