from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr # Changed from username to email to match common login patterns
    password: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    user_type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    hourly_rate: Optional[int] = None
    specialization: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[str] = None # 'client' or 'provider'

class PasswordChange(BaseModel):
    old_password: Optional[str] = None # Optional because OAuth users might not have one
    new_password: str
