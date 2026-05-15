from fastapi import APIRouter, Depends
from app.auth.oauth import get_current_client, get_current_provider
from app.models.user_model import User

router = APIRouter()

@router.get("/client/stats")
async def get_client_stats(client: User = Depends(get_current_client)):
    return {
        "user": client.username,
        "stats": {
            "total_projects": 0,
            "active_services": 0,
            "messages_unread": 0
        }
    }

@router.get("/client/activity")
async def get_client_activity(client: User = Depends(get_current_client)):
    return {
        "user": client.username,
        "activities": []
    }

@router.get("/provider/stats")
async def get_provider_stats(provider: User = Depends(get_current_provider)):
    return {
        "user": provider.username,
        "stats": {
            "total_earnings": 0,
            "active_orders": 0,
            "rating": 5.0
        }
    }

@router.get("/provider/activity")
async def get_provider_activity(provider: User = Depends(get_current_provider)):
    return {
        "user": provider.username,
        "activities": []
    }
