import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database.database import get_db
from app.schemas.auth_schema import UserRegister, Token, UserProfile
from app.services import auth_services
from app.auth.token_utils import create_access_token
from app.auth.google_oauth import oauth
from app.auth.oauth import get_current_user_data
from app.models.user_model import Client, ServiceProvider

router = APIRouter()

# --- Client Auth ---

@router.post("/client/signup", response_model=UserProfile)
def client_signup(data: UserRegister, db: Session = Depends(get_db)):
    client = auth_services.create_client(db, data)
    if not client:
        raise HTTPException(status_code=400, detail="Client with this email already exists")
    return {"username": client.username, "email": client.email, "user_type": "client"}

@router.post("/client/login", response_model=Token)
def client_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client = auth_services.authenticate_client(db, form_data.username, form_data.password)
    if not client:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": client.email, "user_type": "client"})
    return {"access_token": access_token, "token_type": "bearer"}

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
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
    
    email = user_info['email']
    username = user_info.get('name', email.split('@')[0])
    google_id = user_info['sub']
    
    # Retrieve role from session
    role = request.session.get('oauth_role', 'client')
    
    if role == 'client':
        user = auth_services.get_client_by_email(db, email)
        if not user:
            user = Client(username=username, email=email, google_id=google_id, is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        user = auth_services.get_provider_by_email(db, email)
        if not user:
            user = ServiceProvider(username=username, email=email, google_id=google_id, is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email, "user_type": role})
    return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={access_token}&role={role}")

from fastapi.responses import RedirectResponse

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# --- Provider Auth ---

@router.post("/provider/signup", response_model=UserProfile)
def provider_signup(data: UserRegister, db: Session = Depends(get_db)):
    provider = auth_services.create_provider(db, data)
    if not provider:
        raise HTTPException(status_code=400, detail="Provider with this email already exists")
    return {"username": provider.username, "email": provider.email, "user_type": "provider"}

@router.post("/provider/login", response_model=Token)
def provider_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    provider = auth_services.authenticate_provider(db, form_data.username, form_data.password)
    if not provider:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": provider.email, "user_type": "provider"})
    return {"access_token": access_token, "token_type": "bearer"}

# --- SuperAdmin Auth ---

@router.post("/admin/signup", response_model=UserProfile)
def admin_signup(data: UserRegister, db: Session = Depends(get_db)):
    admin = auth_services.create_superadmin(db, data)
    if not admin:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")
    return {"username": admin.username, "email": admin.email, "user_type": "admin"}

@router.post("/admin/login", response_model=Token)
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = auth_services.authenticate_superadmin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": admin.email, "user_type": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify")
async def verify_token(token_data=Depends(get_current_user_data)):
    return {"status": "valid", "user_type": token_data.user_type, "email": token_data.email}

@router.post("/client/logout")
@router.post("/provider/logout")
def logout():
    return {"message": "Successfully logged out"}
