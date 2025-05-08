from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserModel(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    hashed_password: str
    role: UserRole = UserRole.USER
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    solved_problems: List[str] = []  # List of problem IDs
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "solved_problems": []
            }
        }
