# **FastAPI Application with MySQL and Docker**

This project is a modern, containerized FastAPI backend featuring authentication, user management, and MySQL database integration.

---

## **Project Overview**

A robust starter template for building scalable APIs with FastAPI. It includes built-in support for:

- **FastAPI** for high-performance API development.
- **OAuth2 Authentication** for secure user access.
- **MySQL Integration** via SQLAlchemy ORM.
- **Dockerization** for consistent development and deployment environments.

---

## **Folder Structure**

```text
C:\Users\ADMIN\Desktop\ats\
├── app/
│   ├── auth/          # Authentication logic (OAuth2, Tokens)
│   ├── database/      # Database configuration and connection
│   ├── models/        # SQLAlchemy database models
│   ├── routes/        # API endpoints (User, Profile, etc.)
│   ├── schemas/       # Pydantic models for data validation
│   ├── services/      # Business logic and database operations
│   └── main.py        # Application entry point
├── uploads/           # Directory for file storage
├── Dockerfile         # Docker image configuration
├── docker-compose.yml # Multi-container orchestration
└── requirements.txt   # Python dependencies
```

cmd to setup structure
**_mkdir -p app/{auth,database,models,routes,schemas,services} uploads && \
touch app/main.py Dockerfile docker-compose.yml requirements.txt_**

---

## **Quick Start**

### **1. Local Development**

#### **Setup Virtual Environment**

```powershell
# Create venv
python -m venv .venv

# Activate venv
.\venv\Scripts\activate

#packages need to install
pip install fastapi uvicorn sqlalchemy pymysql python-jose passlib bcrypt python-multipart email-validator

#cmd to copy all install packages to requriment.txt
***pip freeze > requirements.txt***

# Upgrade pip
python.exe -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### **Run the Application**

```powershell
uvicorn app.main:app --reload
```

Access the API documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### **2. Dockerization**

Build and run the entire stack (App + MySQL) using Docker Compose.

#### **Run with Docker Compose**

```bash
docker compose up -d --build
```

#### **Core Docker Components**

- **Dockerfile**: Defines the blueprint for the Python application environment.
- **docker-compose.yml**: Orchestrates the FastAPI app and the MySQL database container.

---

## **Authentication & Security**

The project implements **OAuth2 with Password flow and JWT tokens**.

- **Endpoints**:
  - `POST /oauth/token`: Exchange credentials for an access token.
  - `GET /users/me`: Retrieve current authenticated user info.

---

## **Database Management**

Uses **SQLAlchemy** to interface with **MySQL**.

- **Models**: Defined in `app/models/`.
- **Migrations**: Tables are automatically created on application startup.
- **Accessing MySQL Container**:
  ```bash
  docker exec -it ats_db mysql -u root -p
  ```

---

## **Technical Stack**

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLAlchemy
- **Database**: MySQL 8.0
- **Containerization**: Docker & Docker Compose

- **Standard Run**: `docker compose up -d --build`
- **Development Run**: `docker compose --env-file env/.env.dev up --build`
- **Production Run**: `docker compose --env-file env/.env.prod up -d --build`
- **Access MySQL Shell**: `docker exec -it <mysql_container> mysql -u root -p`

** SECRET_KEY Generation **
To generate a secure SECRET_KEY, you should use a method that produces a long, random, and unpredictable string. Here are the two most common ways to do it:

    1 python -c "import secrets; print(secrets.token_hex(32))"

### cmd to run server

```bash
docker compose up --build -d
```

### cmd to stop server

```bash
docker compose down -v
```

### cmd to start server in dev mode

```bash
docker compose --env-file env/.env.dev up --build
```

### cmd to start server in prod mode

```bash
docker compose --env-file env/.env.prod up -d --build
```

<!-- # Production Environment Variables
# ALWAYS USE A SECURE, RANDOMLY GENERATED KEY IN PRODUCTION

APP_PORT=8000

MYSQL_PORT=3307             port from - p
MYSQL_ROOT_PASSWORD=rootpassword      root password
MYSQL_DATABASE=Edttechproddb       database name
MYSQL_USER=myuser                  username
MYSQL_PASSWORD=mypassword          password

DATABASE_URL=mysql+pymysql://myuser:mypassword@localhost:3307/Edttechproddb
 -->

### cmd to access mysql in docker terminal with port number in prod mode

```bash
docker exec -it edtech_mysql mysql -u myuser -p
mypassword
```

Key Implementation Details:

1.  Database Refactoring:
    - Replaced the monolithic User model with separate Client and ServiceProvider models in app/models/user_model.py.
    - Added google_id fields to support OAuth users.

2.  Authentication System:
    - Separate Auth Logic: Created specialized services in app/services/auth_services.py for both Clients and Service Providers.
    - Role-Based JWTs: Updated app/auth/token_utils.py to include user_type in the JWT payload, allowing the backend to correctly identify the user's role on protected  
      requests.
    - Secure Dependencies: Implemented get_current_client and get_current_provider in app/auth/oauth.py for granular access control.

3.  Google OAuth Integration:
    - Backend-Driven Flow: Integrated authlib with FastAPI to handle the OAuth2 redirect and callback flow entirely on the backend.
    - Session Management: Added SessionMiddleware to app/main.py to securely store OAuth state during redirects.
    - OAuth Registry: Created a dedicated app/auth/google_oauth.py module to manage OAuth configurations without circular dependencies.

4.  Comprehensive Routing:
    - Auth Routes: /api/auth/client/... and /api/auth/provider/... for login, signup, logout, and Google OAuth.
    - Profile Routes: /api/users/profile, /api/users/profile/update, and /api/users/settings.
    - Dashboard Routes: Role-specific stats and activity endpoints.
    - Platform Routes: CRUD endpoints for /projects, /services, and /messages.

Next Steps:

- Environment Configuration: Update the placeholder GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your env/.env.dev and env/.env.prod files with your actual credentials from
  the Google Cloud Console.
- Frontend Integration: The backend is now listening on the /api prefix (e.g., http://localhost:8000/api/auth/client/login), which matches your frontend's API_BASE_URL.
- Database Migration: Run the application to allow SQLAlchemy to create the new clients and service_providers tables automatically.

✦ I have implemented the SuperAdmin functionality and the Docker database initialization as requested.

1. SuperAdmin Functionality

- Database Model: Added a SuperAdmin model and a Project model (to track "posted works") in app/models/user_model.py.
- Authentication:
  - Added admin/signup and admin/login endpoints in app/routes/auth_routes.py.
  - Implemented get_current_superadmin dependency in app/auth/oauth.py to protect admin-only routes.
- Monitoring API: Created app/routes/admin_routes.py with endpoints for monitoring:
  - GET /api/admin/stats: Returns total counts of clients, providers, and projects.
  - GET /api/admin/clients: Lists all registered clients.
  - GET /api/admin/providers: Lists all registered service providers.
  - GET /api/admin/projects: Lists all "posted works" (projects).

2. Docker & Database Initialization

- Creation Script: Created scripts/create_tables.py, a standalone Python script that uses your SQLAlchemy models to generate all necessary tables in the database.
- Entrypoint Script: Added scripts/entrypoint.sh to orchestrate the startup process. It runs the table creation script before starting the FastAPI server.
- Dockerfile Update: Modified the Dockerfile to use the entrypoint script, ensuring that whenever you build and run your Docker container, the database schema is
  automatically kept up to date.

The backend is now fully equipped with a multi-role authentication system (Client, Provider, SuperAdmin) and a robust deployment configuration.
