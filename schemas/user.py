from typing import List, Optional
from pydantic import BaseModel
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None