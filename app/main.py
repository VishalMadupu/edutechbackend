import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from app.database.database import engine, Base
from app.models import user_model # Import models to register them with Base
from app.routes import auth_routes, profile_routes, dashboard_routes, platform_routes, admin_routes
from app.auth.google_oauth import oauth

load_dotenv()

# Create database tables
try:
    print(f"Registered tables in metadata: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
except Exception as e:
    print(f"Warning: Could not connect to database for table creation: {e}")

app = FastAPI(title="EdTech Platform API")

# Middleware
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware is required for Authlib OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "your-secret-key")
)

# Include Routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile_routes.router, prefix="/api/users", tags=["Users/Profiles"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(platform_routes.router, prefix="/api", tags=["Platform"]) # Covers /projects, /services, /messages
app.include_router(admin_routes.router, prefix="/api/admin", tags=["SuperAdmin"])

@app.get("/")
def root():
    return {"message": "Welcome to the EdTech Platform API", "docs": "/docs"}
