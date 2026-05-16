import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database.database import get_db
from app.models.user_model import User
from app.schemas.auth_schema import TokenData
from app.auth.token_utils import SECRET_KEY, ALGORITHM

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/client/login") # Default, will be handled by routers

async def get_current_user_data(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if email is None or user_type is None:
            raise credentials_exception
        return TokenData(email=email, user_type=user_type)
    except InvalidTokenError:
        raise credentials_exception

async def get_current_client(
    token_data: Annotated[TokenData, Depends(get_current_user_data)],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_client:
        raise HTTPException(status_code=403, detail="Not authorized as client")
    return user

async def get_current_provider(
    token_data: Annotated[TokenData, Depends(get_current_user_data)],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_provider:
        raise HTTPException(status_code=403, detail="Not authorized as provider/tutor")
    return user

# Aliases for terminology change
get_current_student = get_current_client
get_current_tutor = get_current_provider

async def get_current_superadmin(
    token_data: Annotated[TokenData, Depends(get_current_user_data)],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return user
