from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.edtech_models import Enrollment, Course
from app.schemas.edtech_schema import EnrollmentCreate, Enrollment as EnrollmentSchema
from app.auth.oauth import get_current_user_data

router = APIRouter()

@router.post("/create", response_model=EnrollmentSchema)
def enroll_student(enrollment: EnrollmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    # Check if student already enrolled
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == user.id,
        Enrollment.course_id == enrollment.course_id
    ).first()
    
    if existing:
        return existing
    
    db_enrollment = Enrollment(student_id=user.id, course_id=enrollment.course_id)
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@router.get("/student/{id}", response_model=List[EnrollmentSchema])
def get_student_enrollments(id: int, db: Session = Depends(get_db)):
    return db.query(Enrollment).filter(Enrollment.student_id == id).all()
