from fastapi import APIRouter,status
from .schemas import RegisteredUserSchema
from ..auth.password_handler import PasswordEncrypt

router_users = APIRouter()

@router_users.post("/create",status_code=status.HTTP_201_CREATED)
async def create_user(user:RegisteredUserSchema)->RegisteredUserSchema:
    """Create user"""
    created_user = RegisteredUserSchema(**user.dict())

    return created_user


