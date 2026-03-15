from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class MessageSchema(BaseModel):
    role: str
    content: str

class ChatRequestSchema(BaseModel):
    model: str
    messages: List[MessageSchema]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

class ChatResponseSchema(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
