from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_users():
    return {"message": "GET Request"}


@router.post("/")
def create_user():
    return {"message": "User Created"}


@router.put("/{user_id}")
def update_user(user_id: int):
    return {"message": f"User {user_id} Updated"}


@router.delete("/{user_id}")
def delete_user(user_id: int):
    return {"message": f"User {user_id} Deleted"}