from sqlalchemy import Integer, String, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Profile Fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    bio = Column(String(1000), nullable=True)
    profile_image = Column(String(255), nullable=True)
    
    # Provider Specific Fields (if applicable)
    hourly_rate = Column(Integer, nullable=True)
    specialization = Column(String(255), nullable=True)

    # Role Flags
    is_client = Column(Boolean, default=False)
    is_provider = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Relationships
    projects = relationship("Project", back_populates="client")
    courses = relationship("Course", back_populates="teacher")
    enrollments = relationship("Enrollment", back_populates="student")
    progress_records = relationship("Progress", back_populates="student")

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default="open") # open, in_progress, completed

    client = relationship("User", back_populates="projects")
