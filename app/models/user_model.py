from sqlalchemy import Integer, String, Boolean, Column
from app.database.database import Base

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    google_id = Column(String(255), unique=True, index=True, nullable=True)

class ServiceProvider(Base):
    __tablename__ = 'service_providers'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    google_id = Column(String(255), unique=True, index=True, nullable=True)

class SuperAdmin(Base):
    __tablename__ = 'superadmins'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    client_id = Column(Integer, nullable=False) # Simplified for now, usually a ForeignKey
    status = Column(String(50), default="open") # open, in_progress, completed
