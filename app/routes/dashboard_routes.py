from fastapi import APIRouter, Depends
from app.auth.oauth import get_current_student, get_current_tutor
from app.models.user_model import User

router = APIRouter()

@router.get("/student/stats")
async def get_student_stats(student: User = Depends(get_current_student)):
    return {
        "user": student.username,
        "stats": {
            "total_courses": 0,
            "completed_courses": 0,
            "certificates": 0
        }
    }

@router.get("/student/activity")
async def get_student_activity(student: User = Depends(get_current_student)):
    return {
        "user": student.username,
        "activities": []
    }

@router.get("/tutor/stats")
async def get_tutor_stats(tutor: User = Depends(get_current_tutor)):
    return {
        "user": tutor.username,
        "stats": {
            "total_students": 0,
            "active_courses": 0,
            "rating": 5.0
        }
    }

@router.get("/tutor/activity")
async def get_tutor_activity(tutor: User = Depends(get_current_tutor)):
    return {
        "user": tutor.username,
        "activities": []
    }
