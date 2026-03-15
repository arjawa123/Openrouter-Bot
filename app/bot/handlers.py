from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandObject, Command

from app.db.session import async_session
from app.services import personalization_service, orchestrator
from app.bot.formatter import send_long_message
from loguru import logger

router = Router()

@router.message(Command("code"))
async def handle_code_command(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Please provide a coding prompt. Example: /code write a python function to add numbers")
        return
        
    prompt = command.args
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        async with async_session() as db:
            user = await personalization_service.get_or_create_profile(db, message.from_user)
            response = await orchestrator.process_chat_message(
                db=db,
                user=user,
                chat_id=message.chat.id,
                user_input=prompt,
                mode_override='coder'
            )
            
            await send_long_message(message, response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in code handler: {e}")
        await message.answer("Sorry, an error occurred while processing your request.")

@router.message(F.text)
async def handle_general_message(message: Message):
    if message.text.startswith('/'):
        return # Ignore unknown commands
        
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        async with async_session() as db:
            user = await personalization_service.get_or_create_profile(db, message.from_user)
            response = await orchestrator.process_chat_message(
                db=db,
                user=user,
                chat_id=message.chat.id,
                user_input=message.text
            )
            
            await send_long_message(message, response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in general message handler: {e}")
        await message.answer("Sorry, an error occurred while processing your request.")
