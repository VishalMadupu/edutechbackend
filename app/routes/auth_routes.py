import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from authlib.integrations.starlette_client import OAuthError

from app.database.database import get_db
from app.schemas.auth_schema import UserRegister, Token, UserProfile, UserLogin
from app.services import auth_services
from app.auth.token_utils import create_access_token
from app.auth.google_oauth import oauth
from app.auth.oauth import get_current_user_data
from app.models.user_model import User

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# --- Client Auth ---

@router.post("/client/signup", response_model=UserProfile)
def client_signup(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_services.create_user(db, data, 'client')
    return {"username": user.username, "email": user.email, "user_type": "client"}

@router.post("/client/login", response_model=Token)
def client_login(data: UserLogin, db: Session = Depends(get_db)):
    user = auth_services.authenticate_user(db, data.email, data.password, 'client')
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password, or you do not have client access")
    
    access_token = create_access_token(data={"sub": user.email, "user_type": "client"})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"username": user.username, "email": user.email, "user_type": "client"}
    }

@router.get("/client/oauth")
async def client_oauth(request: Request):
    request.session['oauth_role'] = 'client'
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/provider/oauth")
async def provider_oauth(request: Request):
    request.session['oauth_role'] = 'provider'
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback", name='auth_callback')
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth Error: {e.error}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error during OAuth: {str(e)}")

    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
    
    email = user_info['email']
    username = user_info.get('name', email.split('@')[0])
    google_id = user_info['sub']
    
    # Retrieve role from session
    role = request.session.get('oauth_role', 'client')
    
    try:
        # Find or create user and enable the role
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(username=username, email=email, google_id=google_id, is_active=True)
            db.add(user)
        
        # Apply the role flag
        if role == 'client':
            user.is_client = True
        elif role == 'provider':
            user.is_provider = True
        
        # Update google_id if not set
        if not user.google_id:
            user.google_id = google_id
            
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Database integrity error during user creation")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    access_token = create_access_token(data={"sub": user.email, "user_type": role})
    return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={access_token}&role={role}")

# --- Provider Auth ---

@router.post("/provider/signup", response_model=UserProfile)
def provider_signup(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_services.create_user(db, data, 'provider')
    return {"username": user.username, "email": user.email, "user_type": "provider"}

@router.post("/provider/login", response_model=Token)
def provider_login(data: UserLogin, db: Session = Depends(get_db)):
    user = auth_services.authenticate_user(db, data.email, data.password, 'provider')
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password, or you do not have provider access")

    access_token = create_access_token(data={"sub": user.email, "user_type": "provider"})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"username": user.username, "email": user.email, "user_type": "provider"}
    }

# --- SuperAdmin Auth ---

@router.post("/admin/signup", response_model=UserProfile)
def admin_signup(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_services.create_user(db, data, 'admin')
    return {"username": user.username, "email": user.email, "user_type": "admin"}

@router.post("/admin/login", response_model=Token)
def admin_login(data: UserLogin, db: Session = Depends(get_db)):
    user = auth_services.authenticate_user(db, data.email, data.password, 'admin')
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password, or you do not have admin access")

    access_token = create_access_token(data={"sub": user.email, "user_type": "admin"})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"username": user.username, "email": user.email, "user_type": "admin"}
    }


@router.get("/verify")
async def verify_token(token_data=Depends(get_current_user_data)):
    return {"status": "valid", "user_type": token_data.user_type, "email": token_data.email}

@router.post("/client/logout")
@router.post("/provider/logout")
def logout():
    return {"message": "Successfully logged out"}
