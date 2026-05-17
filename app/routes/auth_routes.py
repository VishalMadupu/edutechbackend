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

# --- Student Auth ---

@router.post("/student/signup", response_model=UserProfile)
def student_signup(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_services.create_user(db, data, 'student')
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "user_type": "student",
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "bio": user.bio,
        "profile_image": user.profile_image
    }

@router.post("/student/login", response_model=Token)
def student_login(data: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    user = auth_services.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found. Please sign up first.")
    
    # Check if user has student role (is_client)
    if not user.is_client:
        raise HTTPException(status_code=403, detail="This account is not registered as a learner. Please sign up as a student.")

    # Check if user has a password (might be OAuth-only)
    if not user.hashed_password:
        raise HTTPException(status_code=400, detail="This account uses Google Login. Please use the Google button.")

    # Verify password
    from app.auth.token_utils import verify_password
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
    
    access_token = create_access_token(data={"sub": user.email, "user_type": "student"})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_type": "student",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "bio": user.bio,
            "profile_image": user.profile_image
        }
    }

@router.get("/student/oauth")
async def student_oauth(request: Request, mode: str = "login"):
    request.session['oauth_role'] = 'student'
    request.session['oauth_mode'] = mode
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for('auth_callback')
    response = await oauth.google.authorize_redirect(request, redirect_uri)
    # Set a temporary cookie as a backup for the mode
    response.set_cookie(key="oauth_mode", value=mode, max_age=600)
    return response

@router.get("/tutor/oauth")
async def tutor_oauth(request: Request, mode: str = "login"):
    request.session['oauth_role'] = 'tutor'
    request.session['oauth_mode'] = mode
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for('auth_callback')
    response = await oauth.google.authorize_redirect(request, redirect_uri)
    # Set a temporary cookie as a backup for the mode
    response.set_cookie(key="oauth_mode", value=mode, max_age=600)
    return response

@router.get("/student/oauth-url")
async def get_student_oauth_url(request: Request):
    request.session['oauth_role'] = 'student'
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for('auth_callback')
    auth_response = await oauth.google.authorize_redirect(request, redirect_uri)
    return {"url": auth_response.headers.get("Location")}

@router.get("/tutor/oauth-url")
async def get_tutor_oauth_url(request: Request):
    request.session['oauth_role'] = 'tutor'
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or request.url_for('auth_callback')
    auth_response = await oauth.google.authorize_redirect(request, redirect_uri)
    return {"url": auth_response.headers.get("Location")}

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
    
    # Retrieve role and mode from session, with cookie fallback
    role = request.session.get('oauth_role', 'student')
    mode = request.session.get('oauth_mode') or request.cookies.get('oauth_mode', 'login')
    is_new_user = False
    
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            if mode == 'signup':
                # Create user if in signup mode
                user = User(username=username, email=email, google_id=google_id, is_active=True)
                db.add(user)
                is_new_user = True
            else:
                # If user not found and not in signup mode, redirect to login with error
                error_msg = "Account not found. Please sign up with this email first."
                if role == 'tutor':
                    error_msg = "Tutor account not found. Please apply first."
                
                from urllib.parse import quote
                return RedirectResponse(url=f"{FRONTEND_URL}/{role}/login?error={quote(error_msg)}")

        # Enforce RBAC logic
        if mode == 'signup':
            # Enable the requested role flag during signup
            if role == 'student':
                user.is_client = True
            elif role == 'tutor':
                user.is_provider = True
        else:
            # During LOGIN mode, we MUST verify they already have the role
            if role == 'student' and not user.is_client:
                error_msg = "Account exists, but you are not registered as a learner. Please sign up as a student first."
                from urllib.parse import quote
                return RedirectResponse(url=f"{FRONTEND_URL}/student/login?error={quote(error_msg)}")
            
            if role == 'tutor' and not user.is_provider:
                error_msg = "You are not registered as a tutor. Please apply through the signup page."
                from urllib.parse import quote
                return RedirectResponse(url=f"{FRONTEND_URL}/tutor/login?error={quote(error_msg)}")

        # Update google_id if not set
        if not user.google_id:
            user.google_id = google_id
            
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    access_token = create_access_token(data={"sub": user.email, "user_type": role})
    response = RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={access_token}&role={role}&new_user={str(is_new_user).lower()}")
    # Clean up the backup cookie
    response.delete_cookie(key="oauth_mode")
    return response

# --- Tutor Auth ---

@router.post("/tutor/signup", response_model=UserProfile)
def tutor_signup(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_services.create_user(db, data, 'tutor')
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "user_type": "tutor",
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "bio": user.bio,
        "profile_image": user.profile_image,
        "hourly_rate": user.hourly_rate,
        "specialization": user.specialization
    }

@router.post("/tutor/login", response_model=Token)
def tutor_login(data: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    user = auth_services.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found. Please apply to become a tutor.")
    
    # Check if user has tutor role (is_provider)
    if not user.is_provider:
        raise HTTPException(status_code=403, detail="This account is not registered as a tutor. Please register as a teacher.")

    # Check if user has a password (might be OAuth-only)
    if not user.hashed_password:
        raise HTTPException(status_code=400, detail="This account uses Google Login. Please use the Google button.")

    # Verify password
    from app.auth.token_utils import verify_password
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")

    access_token = create_access_token(data={"sub": user.email, "user_type": "tutor"})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_type": "tutor",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "bio": user.bio,
            "profile_image": user.profile_image,
            "hourly_rate": user.hourly_rate,
            "specialization": user.specialization
        }
    }

# --- SuperAdmin Auth ---

@router.post("/admin/signup", response_model=UserProfile)
def admin_signup(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_services.create_user(db, data, 'admin')
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "user_type": "admin",
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "bio": user.bio,
        "profile_image": user.profile_image
    }

@router.post("/admin/login", response_model=Token)
def admin_login(data: UserLogin, db: Session = Depends(get_db)):
    user = auth_services.authenticate_user(db, data.email, data.password, 'admin')
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password, or you do not have admin access")

    access_token = create_access_token(data={"sub": user.email, "user_type": "admin"})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_type": "admin",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "bio": user.bio,
            "profile_image": user.profile_image
        }
    }


@router.get("/verify")
async def verify_token(token_data=Depends(get_current_user_data)):
    return {"status": "valid", "user_type": token_data.user_type, "email": token_data.email}

@router.post("/student/logout")
@router.post("/tutor/logout")
@router.post("/admin/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Successfully logged out"}

@router.get("/debug-oauth")
async def debug_oauth():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "NOT FOUND")
    return {
        "google_client_id_prefix": client_id[:12] if client_id != "NOT FOUND" else "N/A",
        "google_redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "NOT FOUND"),
        "frontend_url": FRONTEND_URL
    }
