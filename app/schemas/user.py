from pydantic import BaseModel
from typing import Optional

class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    preferred_name: Optional[str] = None
    language: Optional[str] = None
    style: Optional[str] = None
    default_mode: Optional[str] = None
    default_model: Optional[str] = None
