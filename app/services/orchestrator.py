from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.models import User
from app.services.intent_service import intent_service, Intent
from app.services.assistant_service import assistant_service
from app.services.todo_service import todo_service
from app.services.notes_service import notes_service
from app.services.memory_service import memory_service

async def process_chat_message(
    db: AsyncSession, 
    user: User, 
    chat_id: int, 
    user_input: str,
    mode_override: str = None
) -> str:
    """
    Enhanced orchestrator that detects intent and routes to the appropriate service.
    """
    # 1. Detect Intent
    intent = await intent_service.detect_intent(user_input)
    logger.info(f"Detected intent: {intent} for user {user.id}")

    additional_context = ""
    
    # 2. Proactive Routing & Action Execution
    if intent == Intent.TASK_ADD:
        task_data = await intent_service.extract_entity(intent, user_input)
        content = task_data.get("content")
        due_at_str = task_data.get("due_at")
        
        due_at = None
        if due_at_str:
            from datetime import datetime
            try:
                # Handle various ISO formats from LLM
                due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
            except Exception as e:
                logger.error(f"Failed to parse due_at '{due_at_str}': {e}")

        await crud.create_todo(db, user.id, content, due_at=due_at)
        
        due_info = f" (due at {due_at_str})" if due_at_str else ""
        additional_context = f"ACTION SUCCESS: I have added this task to your list: '{content}'{due_info}"
        logger.info(f"Task added for user {user.id}: {content}{due_info}")
        
    elif intent == Intent.NOTE_ADD:
        note_data = await intent_service.extract_entity(intent, user_input)
        content = note_data.get("content")
        await crud.create_note(db, user.id, content)
        additional_context = f"ACTION SUCCESS: I have saved this note for you: '{content}'"
        logger.info(f"Note added for user {user.id}: {content}")
        
    elif intent == Intent.REMEMBER:
        memory_data = await intent_service.extract_entity(intent, user_input)
        content = memory_data.get("content")
        await crud.create_memory(db, user.id, content)
        additional_context = f"ACTION SUCCESS: I have remembered this for you: '{content}'"
        logger.info(f"Fact remembered for user {user.id}: {content}")

    # 3. Use AssistantService for natural language interaction
    # If an action was performed, the assistant will know via 'additional_context'
    return await assistant_service.chat(
        db=db,
        user=user,
        chat_id=chat_id,
        user_input=user_input,
        mode_override=mode_override,
        additional_context=additional_context
    )
