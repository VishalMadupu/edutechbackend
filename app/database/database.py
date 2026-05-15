from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable if available, otherwise fallback to local SQLite
Database_URL = os.getenv("DATABASE_URL", "sqlite:///./edtech.db")

if Database_URL.startswith("sqlite"):
    engine = create_engine(Database_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(Database_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

