from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.oauth import get_current_user_data, get_current_client, get_current_provider
from app.schemas.auth_schema import UserProfile, PasswordChange
from app.models.user_model import Client, ServiceProvider, SuperAdmin
from app.auth.token_utils import verify_password
from app.services import auth_services

router = APIRouter()

@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    token_data = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    if token_data.user_type == "client":
        user = db.query(Client).filter(Client.email == token_data.email).first()
    elif token_data.user_type == "provider":
        user = db.query(ServiceProvider).filter(ServiceProvider.email == token_data.email).first()
    elif token_data.user_type == "admin":
        user = db.query(SuperAdmin).filter(SuperAdmin.email == token_data.email).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
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
    if token_data.user_type == "client":
        user = db.query(Client).filter(Client.email == token_data.email).first()
    else:
        user = db.query(ServiceProvider).filter(ServiceProvider.email == token_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user.username,
        "email": user.email,
        "user_type": token_data.user_type
    }

@router.put("/profile/update")
async def update_profile(
    data: dict, # Simplified for now
    token_data = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    if token_data.user_type == "client":
        user = db.query(Client).filter(Client.email == token_data.email).first()
    else:
        user = db.query(ServiceProvider).filter(ServiceProvider.email == token_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if "username" in data:
        user.username = data["username"]
    
    db.commit()
    return {"message": "Profile updated successfully"}

@router.get("/settings")
async def get_settings(token_data = Depends(get_current_user_data)):
    return {"message": f"Settings for {token_data.user_type}", "email": token_data.email}
