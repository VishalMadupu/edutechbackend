from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user_model import Client, ServiceProvider
from app.auth.token_utils import hash_password, verify_password

# --- Client Services ---
def create_client(db: Session, data):
    existing_user = db.query(Client).filter(Client.email == data.email).first()
    if existing_user:
        return None
    new_client = Client(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password) if data.password else None
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

def authenticate_client(db: Session, username_or_email: str, password: str):
    client = db.query(Client).filter(
        or_(Client.username == username_or_email, Client.email == username_or_email)
    ).first()
    if not client or not client.hashed_password:
        return None
    if not verify_password(password, client.hashed_password):
        return None
    return client

def get_client_by_email(db: Session, email: str):
    return db.query(Client).filter(Client.email == email).first()

# --- Provider Services ---
def create_provider(db: Session, data):
    existing_user = db.query(ServiceProvider).filter(ServiceProvider.email == data.email).first()
    if existing_user:
        return None
    new_provider = ServiceProvider(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password) if data.password else None
    )
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return new_provider

def authenticate_provider(db: Session, username_or_email: str, password: str):
    provider = db.query(ServiceProvider).filter(
        or_(ServiceProvider.username == username_or_email, ServiceProvider.email == username_or_email)
    ).first()
    if not provider or not provider.hashed_password:
        return None
    if not verify_password(password, provider.hashed_password):
        return None
    return provider

def get_provider_by_email(db: Session, email: str):
    return db.query(ServiceProvider).filter(ServiceProvider.email == email).first()

# --- SuperAdmin Services ---
from app.models.user_model import SuperAdmin

def create_superadmin(db: Session, data):
    existing_user = db.query(SuperAdmin).filter(SuperAdmin.email == data.email).first()
    if existing_user:
        return None
    new_admin = SuperAdmin(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

def authenticate_superadmin(db: Session, username_or_email: str, password: str):
    admin = db.query(SuperAdmin).filter(
        or_(SuperAdmin.username == username_or_email, SuperAdmin.email == username_or_email)
    ).first()
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin

def update_password(db: Session, user, new_password: str):
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return True
