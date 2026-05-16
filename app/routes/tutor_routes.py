from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.user_model import User
from app.models.edtech_models import Course
from app.schemas.edtech_schema import TutorProfile, Course as CourseSchema

router = APIRouter()

@router.get("/", response_model=List[TutorProfile])
def get_all_tutors(db: Session = Depends(get_db)):
    return db.query(User).filter(User.is_provider == True).all()

@router.get("/{id}", response_model=TutorProfile)
def get_tutor_profile(id: int, db: Session = Depends(get_db)):
    tutor = db.query(User).filter(User.id == id, User.is_provider == True).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return tutor

@router.get("/{id}/courses", response_model=List[CourseSchema])
def get_tutor_courses(id: int, db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.teacher_id == id).all()
