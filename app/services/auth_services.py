from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user_model import User
from app.auth.token_utils import hash_password, verify_password

# --- Unified User Services ---

def create_user(db: Session, data, role: str):
    """
    Finds an existing user by email or creates a new one.
    Updates the user to have the specified role flag.
    """
    user = db.query(User).filter(User.email == data.email).first()
    
    username = getattr(data, 'username', None)
    if not username:
        username = data.email.split('@')[0]

    if not user:
        # Create new user
        user = User(
            username=username,
            email=data.email,
            hashed_password=hash_password(data.password) if hasattr(data, 'password') and data.password else None,
            is_active=True
        )
        db.add(user)
    
    # Enable the specific role
    if role in ['client', 'student']:
        user.is_client = True
    elif role in ['provider', 'tutor']:
        user.is_provider = True
    elif role == 'admin':
        user.is_admin = True
    
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str, required_role: str):
    """
    Authenticates a user and verifies they have the required role flag.
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not user.hashed_password:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
        
    # Check role flag
    if required_role in ['client', 'student'] and not user.is_client:
        return None
    if required_role in ['provider', 'tutor'] and not user.is_provider:
        return None
    if required_role == 'admin' and not user.is_admin:
        return None
        
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# --- Legacy Compatibility Wrappers (for Routes) ---

def create_client(db: Session, data):
    return create_user(db, data, 'client')

def create_provider(db: Session, data):
    return create_user(db, data, 'provider')

def create_superadmin(db: Session, data):
    return create_user(db, data, 'admin')

def authenticate_client(db: Session, email: str, password: str):
    return authenticate_user(db, email, password, 'client')

def authenticate_provider(db: Session, email: str, password: str):
    return authenticate_user(db, email, password, 'provider')

def authenticate_superadmin(db: Session, email: str, password: str):
    return authenticate_user(db, email, password, 'admin')

def get_client_by_email(db: Session, email: str):
    user = get_user_by_email(db, email)
    return user if user and user.is_client else None

def get_provider_by_email(db: Session, email: str):
    user = get_user_by_email(db, email)
    return user if user and user.is_provider else None

def update_password(db: Session, user, new_password: str):
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return True
