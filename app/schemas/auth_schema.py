from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr # Changed from username to email to match common login patterns
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[str] = None # 'client' or 'provider'

class UserProfile(BaseModel):
    username: str
    email: str
    user_type: str

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    old_password: Optional[str] = None # Optional because OAuth users might not have one
    new_password: str
