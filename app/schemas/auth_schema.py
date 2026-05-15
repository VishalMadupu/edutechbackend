from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
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
