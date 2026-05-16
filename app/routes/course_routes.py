from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.edtech_models import Course
from app.schemas.edtech_schema import CourseCreate, Course as CourseSchema
from app.auth.oauth import get_current_user_data

router = APIRouter()

@router.post("/create", response_model=CourseSchema)
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    if current_user.user_type not in ['tutor', 'provider', 'admin']:
        raise HTTPException(status_code=403, detail="Only tutors can create courses")
    
    # Get user object to get ID
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    
    db_course = Course(**course.dict(), teacher_id=user.id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseSchema])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.get("/{id}", response_model=CourseSchema)
def get_course(id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{id}", response_model=CourseSchema)
def update_course(id: int, course_data: CourseCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    db_course = db.query(Course).filter(Course.id == id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check ownership
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    if db_course.teacher_id != user.id and current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to update this course")
    
    for key, value in course_data.dict().items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{id}")
def delete_course(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    db_course = db.query(Course).filter(Course.id == id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check ownership
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    if db_course.teacher_id != user.id and current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete this course")
    
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted successfully"}

@router.get("/free", response_model=List[CourseSchema])
def get_free_courses(db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.is_free == True).all()

@router.get("/paid", response_model=List[CourseSchema])
def get_paid_courses(db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.is_free == False).all()

@router.get("/category/{category}", response_model=List[CourseSchema])
def get_courses_by_category(category: str, db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.category == category).all()
