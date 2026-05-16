from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.edtech_models import Video, Course
from app.schemas.edtech_schema import VideoCreate, Video as VideoSchema
from app.auth.oauth import get_current_user_data

router = APIRouter()

@router.post("/upload", response_model=VideoSchema)
def upload_video(video: VideoCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    # Check if course exists and belongs to tutor
    course = db.query(Course).filter(Course.id == video.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    if course.teacher_id != user.id and current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to add videos to this course")
    
    db_video = Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.post("/youtube", response_model=VideoSchema)
def add_youtube_video(video: VideoCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    # Same logic as upload for now, maybe some YouTube specific validation later
    return upload_video(video, db, current_user)

@router.get("/{id}", response_model=VideoSchema)
def get_video_details(id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.delete("/{id}")
def delete_video(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user_data)):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    course = db.query(Course).filter(Course.id == video.course_id).first()
    from app.models.user_model import User
    user = db.query(User).filter(User.email == current_user.email).first()
    if course.teacher_id != user.id and current_user.user_type != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")
    
    db.delete(video)
    db.commit()
    return {"message": "Video deleted successfully"}
