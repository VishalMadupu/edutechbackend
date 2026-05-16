from sqlalchemy import Integer, String, Boolean, Column, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=True)
    thumbnail = Column(String(255), nullable=True)
    price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="courses")
    videos = relationship("Video", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    video_url = Column(String(255), nullable=True)
    youtube_url = Column(String(255), nullable=True)
    duration = Column(String(50), nullable=True)
    title = Column(String(255), nullable=False)

    course = relationship("Course", back_populates="videos")
    progress_records = relationship("Progress", back_populates="video", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    watched_duration = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)

    student = relationship("User", back_populates="progress_records")
    video = relationship("Video", back_populates="progress_records")
