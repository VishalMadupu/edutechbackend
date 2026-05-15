from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.oauth import get_current_superadmin
from app.models.user_model import User, Project

router = APIRouter()

@router.get("/stats")
async def get_platform_stats(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    total_clients = db.query(User).filter(User.is_client == True).count()
    total_providers = db.query(User).filter(User.is_provider == True).count()
    total_projects = db.query(Project).count()
    
    return {
        "total_clients": total_clients,
        "total_providers": total_providers,
        "total_projects": total_projects,
        "active_admin": admin.username
    }

@router.get("/clients")
async def list_all_clients(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    # Fetch all users where is_client is True with detailed profile
    clients = db.query(User).filter(User.is_client == True).all()
    return clients

@router.get("/providers")
async def list_all_providers(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    # Fetch all users where is_provider is True with detailed profile
    providers = db.query(User).filter(User.is_provider == True).all()
    return providers

@router.get("/projects")
async def list_all_projects(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    projects = db.query(Project).all()
    return projects
