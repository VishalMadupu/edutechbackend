from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.oauth import get_current_superadmin
from app.models.user_model import User
from app.models.edtech_models import Course

router = APIRouter()

@router.get("/stats")
async def get_platform_stats(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    total_students = db.query(User).filter(User.is_client == True).count()
    total_tutors = db.query(User).filter(User.is_provider == True).count()
    total_courses = db.query(Course).count()
    
    return {
        "total_clients": total_students,
        "total_providers": total_tutors,
        "total_projects": total_courses,
        "active_admin": admin.username
    }

@router.get("/students")
async def list_all_students(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    students = db.query(User).filter(User.is_client == True).all()
    return students

@router.get("/tutors")
async def list_all_tutors(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    tutors = db.query(User).filter(User.is_provider == True).all()
    return tutors

@router.get("/courses")
async def list_all_courses(
    admin: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    courses = db.query(Course).all()
    return courses
