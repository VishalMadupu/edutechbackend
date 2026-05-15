import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.database.database import engine, Base
from app.models import user_model
from app.routes import (
    auth_routes,
    profile_routes,
    dashboard_routes,
    platform_routes,
    admin_routes
)

load_dotenv()

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

try:
    print(f"Registered tables in metadata: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
except Exception as e:
    print(f"Warning: Could not connect to database for table creation: {e}")

# --------------------------------------------------
# APP
# --------------------------------------------------

app = FastAPI(title="EdTech Platform API")

# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

ENV = os.getenv("ENV", "development")
IS_PROD = ENV == "production"

print(f"Running Environment: {ENV}")
print(f"Production Mode: {IS_PROD}")

# --------------------------------------------------
# CORS
# --------------------------------------------------

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://edu-ten-mu.vercel.app",
    "https://edu-ten-mu.vercel.app/",
]

# IMPORTANT:
# CORS should be added BEFORE SessionMiddleware
# for proper cross-site cookie handling

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# SESSION MIDDLEWARE
# --------------------------------------------------

# Required for Authlib OAuth state/session handling
# Cross-domain OAuth requires:
# same_site="none"
# https_only=True

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
    same_site="none" if IS_PROD else "lax",
    https_only=IS_PROD,
    max_age=3600,
)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    profile_routes.router,
    prefix="/api/users",
    tags=["Users/Profiles"]
)

app.include_router(
    dashboard_routes.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    platform_routes.router,
    prefix="/api",
    tags=["Platform"]
)

app.include_router(
    admin_routes.router,
    prefix="/api/admin",
    tags=["SuperAdmin"]
)

# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to the EdTech Platform API",
        "docs": "/docs"
    }
