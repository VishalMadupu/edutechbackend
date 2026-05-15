from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.oauth import get_current_user_data
from app.schemas.auth_schema import UserProfile, PasswordChange
from app.models.user_model import User
from app.auth.token_utils import verify_password
from app.services import auth_services

router = APIRouter()

@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    token_data = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If user has an existing password, they must provide it correctly
    if user.hashed_password:
        if not data.old_password:
            raise HTTPException(status_code=400, detail="Old password is required to set a new one")
        if not verify_password(data.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect old password")
    
    auth_services.update_password(db, user, data.new_password)
    return {"message": "Password updated successfully"}

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    token_data = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user.username,
        "email": user.email,
        "user_type": token_data.user_type,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "bio": user.bio,
        "hourly_rate": user.hourly_rate,
        "specialization": user.specialization
    }

@router.put("/profile/update")
async def update_profile(
    data: dict,
    token_data = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    allowed_fields = [
        "username", "first_name", "last_name", "phone_number", 
        "bio", "hourly_rate", "specialization"
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.commit()
    db.refresh(user)
    return {"message": "Profile updated successfully"}

@router.get("/settings")
async def get_settings(token_data = Depends(get_current_user_data)):
    return {"message": f"Settings for {token_data.user_type}", "email": token_data.email}
