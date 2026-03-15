import re

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2 format."""
    # Characters that need escaping in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    # Escape them
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def chunk_text(text: str, max_length: int = 4000) -> list[str]:
    """Splits text into chunks of maximum length."""
    if not text:
        return []
        
    chunks = []
    while len(text) > max_length:
        # Find the last newline within the max_length limit
        split_index = text.rfind('\n', 0, max_length)
        if split_index == -1:
            # If no newline found, just split at max_length
            split_index = max_length
        
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
        
    if text:
        chunks.append(text)
        
    return chunks
