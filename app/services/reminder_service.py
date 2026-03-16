import asyncio
from datetime import datetime, timezone
from loguru import logger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import async_session
from app.db.models import Todo, User
from aiogram import Bot

async def reminder_worker(bot: Bot):
    """
    Background task to check for due todos and notify users.
    """
    logger.info("Starting Reminder Worker...")
    while True:
        try:
            async with async_session() as db:
                now = datetime.now(timezone.utc)
                
                # Fetch pending todos that are past due and not yet notified
                stmt = select(Todo).options(selectinload(Todo.user)).where(
                    Todo.status == "pending",
                    Todo.due_at <= now,
                    Todo.is_notified == False
                )
                
                result = await db.execute(stmt)
                due_todos = result.scalars().all()
                
                for todo in due_todos:
                    user = todo.user
                    if not user:
                        continue
                        
                    try:
                        message = (
                            f"⏰ *REMINDER*\n\n"
                            f"Task: `{todo.text}`\n"
                            f"Due at: {todo.due_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                            f"Reply to this to update status."
                        )
                        
                        await bot.send_message(chat_id=user.telegram_user_id, text=message)
                        
                        # Mark as notified
                        todo.is_notified = True
                        await db.commit()
                        logger.info(f"Notification sent for todo {todo.id} to user {user.id}")
                        
                    except Exception as e:
                        logger.error(f"Failed to send notification for todo {todo.id}: {e}")
            
            # Check every 60 seconds
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Reminder worker error: {e}")
            await asyncio.sleep(60)
