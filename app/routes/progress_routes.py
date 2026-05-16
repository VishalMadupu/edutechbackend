from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.edtech_models import Progress
from app.schemas.edtech_schema import ProgressUpdate, Progress as ProgressSchema
from app.auth.oauth import get_current_user_data

router = APIRouter()

@router.post("/update", response_model=ProgressSchema)
def update_progress(progress: ProgressUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    
    db_progress = db.query(Progress).filter(
        Progress.student_id == user.id,
        Progress.video_id == progress.video_id
    ).first()
    
    if db_progress:
        db_progress.watched_duration = progress.watched_duration
        db_progress.completed = progress.completed
    else:
        db_progress = Progress(
            student_id=user.id,
            video_id=progress.video_id,
            watched_duration=progress.watched_duration,
            completed=progress.completed
        )
        db.add(db_progress)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.get("/{studentId}", response_model=List[ProgressSchema])
def get_learner_progress(studentId: int, db: Session = Depends(get_db)):
    return db.query(Progress).filter(Progress.student_id == studentId).all()
