from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.auth.oauth import get_current_user_data

router = APIRouter()

# --- Projects ---

@router.get("/projects")
async def list_projects(token_data = Depends(get_current_user_data)):
    return {"projects": []}

@router.post("/projects/create")
async def create_project(data: dict, token_data = Depends(get_current_user_data)):
    return {"message": "Project created", "data": data}

@router.get("/projects/{project_id}")
async def get_project_details(project_id: str, token_data = Depends(get_current_user_data)):
    return {"project_id": project_id, "title": "Sample Project"}

@router.put("/projects/{project_id}/update")
async def update_project(project_id: str, data: dict, token_data = Depends(get_current_user_data)):
    return {"message": f"Project {project_id} updated"}

@router.delete("/projects/{project_id}/delete")
async def delete_project(project_id: str, token_data = Depends(get_current_user_data)):
    return {"message": f"Project {project_id} deleted"}

# --- Services ---

@router.get("/services")
async def list_services():
    return {"services": []}

@router.post("/services/create")
async def create_service(data: dict, token_data = Depends(get_current_user_data)):
    if token_data.user_type != "provider":
        raise HTTPException(status_code=403, detail="Only providers can create services")
    return {"message": "Service created", "data": data}

@router.get("/services/{service_id}")
async def get_service_details(service_id: str):
    return {"service_id": service_id, "title": "Sample Service"}

# --- Messages ---

@router.get("/messages")
async def list_messages(token_data = Depends(get_current_user_data)):
    return {"messages": []}

@router.post("/messages/send")
async def send_message(data: dict, token_data = Depends(get_current_user_data)):
    return {"message": "Message sent", "data": data}

@router.get("/messages/{conversation_id}")
async def get_conversation(conversation_id: str, token_data = Depends(get_current_user_data)):
    return {"conversation_id": conversation_id, "messages": []}
