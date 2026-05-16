from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VideoBase(BaseModel):
    title: str
    video_url: Optional[str] = None
    youtube_url: Optional[str] = None
    duration: Optional[str] = None

class VideoCreate(VideoBase):
    course_id: int

class Video(VideoBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    thumbnail: Optional[str] = None
    price: float = 0.0
    is_free: bool = True

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    teacher_id: int
    created_at: datetime
    videos: List[Video] = []

    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    course_id: int

class Enrollment(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime
    course: Optional[Course] = None

    class Config:
        from_attributes = True

class ProgressUpdate(BaseModel):
    video_id: int
    watched_duration: float
    completed: bool = False

class Progress(BaseModel):
    id: int
    student_id: int
    video_id: int
    watched_duration: float
    completed: bool

    class Config:
        from_attributes = True

class TutorProfile(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    specialization: Optional[str] = None

    class Config:
        from_attributes = True
