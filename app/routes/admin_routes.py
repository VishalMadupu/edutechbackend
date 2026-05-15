from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.oauth import get_current_superadmin
from app.models.user_model import Client, ServiceProvider, Project, SuperAdmin

router = APIRouter()

@router.get("/stats")
async def get_platform_stats(
    admin: SuperAdmin = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    total_clients = db.query(Client).count()
    total_providers = db.query(ServiceProvider).count()
    total_projects = db.query(Project).count()
    
    return {
        "total_clients": total_clients,
        "total_providers": total_providers,
        "total_projects": total_projects,
        "active_admin": admin.username
    }

@router.get("/clients")
async def list_all_clients(
    admin: SuperAdmin = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    clients = db.query(Client).all()
    return clients

@router.get("/providers")
async def list_all_providers(
    admin: SuperAdmin = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    providers = db.query(ServiceProvider).all()
    return providers

@router.get("/projects")
async def list_all_projects(
    admin: SuperAdmin = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    projects = db.query(Project).all()
    return projects
