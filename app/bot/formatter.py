from app.utils.text import chunk_text

async def send_long_message(message, text: str, **kwargs):
    """Helper to send long messages by chunking them."""
    chunks = chunk_text(text)
    for chunk in chunks:
        await message.answer(chunk, **kwargs)
