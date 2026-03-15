from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject

from app.db.session import async_session
from app.services import personalization_service, memory_service, todo_service, notes_service, snippet_service, digest_service
from app.bot.formatter import send_long_message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        text = f"Hello {user.preferred_name or user.first_name}!\nI am your AI Assistant powered by OpenRouter.\nType /help to see what I can do."
        await message.answer(text)

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
*General Commands*
/start - Start the bot
/help - Show this help message
/profile - View your profile
/mode <assistant|coder|researcher|planner> - Change AI mode

*Memory*
/remember <text> - Save a memory
/forget <keyword> - Forget a memory
/memory - View recent memories

*Tools*
/note <text> - Save a note
/notes - List notes
/todo add <text> - Add a todo
/todo list - List pending todos
/todo done <id> - Mark todo as done
/snippet save <name> <text> - Save snippet
/snippet get <name> - Get snippet
/digest - View daily digest
/code <prompt> - Fast access to coder mode
"""
    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        text = f"*Your Profile*\nName: {user.preferred_name or user.first_name}\nMode: {user.default_mode}\nLanguage: {user.language}"
        await message.answer(text, parse_mode="Markdown")

@router.message(Command("mode"))
async def cmd_mode(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Please specify a mode: assistant, coder, researcher, or planner.\nUsage: /mode coder")
        return
        
    mode = command.args.strip().lower()
    valid_modes = ['assistant', 'coder', 'researcher', 'planner']
    if mode not in valid_modes:
        await message.answer(f"Invalid mode. Choose from: {', '.join(valid_modes)}")
        return
        
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        await personalization_service.update_profile(db, user.id, default_mode=mode)
        await message.answer(f"Mode set to: {mode}")

@router.message(Command("remember"))
async def cmd_remember(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /remember <text>")
        return
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        res = await memory_service.remember(db, user.id, command.args)
        await message.answer(res)

@router.message(Command("forget"))
async def cmd_forget(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /forget <keyword>")
        return
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        res = await memory_service.forget(db, user.id, command.args.strip())
        await message.answer(res)

@router.message(Command("memory"))
async def cmd_memory(message: Message):
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        res = await memory_service.get_memories_context(db, user.id)
        if not res:
            res = "You have no memories."
        await message.answer(res)

@router.message(Command("todo"))
async def cmd_todo(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage:\n/todo add <text>\n/todo list\n/todo done <id>")
        return
        
    parts = command.args.split(maxsplit=1)
    action = parts[0].lower()
    
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        
        if action == "add" and len(parts) > 1:
            res = await todo_service.add_todo(db, user.id, parts[1])
            await message.answer(res)
        elif action == "list":
            res = await todo_service.list_todos(db, user.id)
            await message.answer(res)
        elif action == "done" and len(parts) > 1 and parts[1].isdigit():
            res = await todo_service.mark_done(db, user.id, int(parts[1]))
            await message.answer(res)
        else:
            await message.answer("Invalid todo command.")

@router.message(Command("note"))
async def cmd_note(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /note <text>")
        return
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        res = await notes_service.add_note(db, user.id, command.args)
        await message.answer(res)

@router.message(Command("notes"))
async def cmd_notes(message: Message):
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        res = await notes_service.list_notes(db, user.id)
        await message.answer(res)

@router.message(Command("digest"))
async def cmd_digest(message: Message):
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        res = await digest_service.generate_digest(db, user)
        await message.answer(res, parse_mode="Markdown")

@router.message(Command("snippet"))
async def cmd_snippet(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage:\n/snippet save <name> <content>\n/snippet get <name>")
        return
    
    parts = command.args.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("Invalid format.")
        return
        
    action = parts[0].lower()
    name = parts[1]
    
    async with async_session() as db:
        user = await personalization_service.get_or_create_profile(db, message.from_user)
        
        if action == "save" and len(parts) == 3:
            res = await snippet_service.save_snippet(db, user.id, name, parts[2])
            await message.answer(res)
        elif action == "get":
            res = await snippet_service.get_snippet(db, user.id, name)
            await message.answer(res, parse_mode="Markdown")
        else:
            await message.answer("Invalid snippet command.")
