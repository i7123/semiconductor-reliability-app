from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: Optional[str]
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UsageStatus(BaseModel):
    daily_usage: int
    daily_limit: int
    is_premium: bool
    usage_remaining: int
    reset_time: datetime

class AuthorizationRequired(BaseModel):
    error: str
    message: str
    requires_auth: bool
    upgrade_needed: bool