import socket
from fastapi import APIRouter
from settings import settings

info_router = APIRouter()



@info_router.get("/backend")
async def get_backend():
    """Get data from backend"""
    return {"Return from backend": socket.gethostname()}

@info_router.get("/database")
async def get_database():
    """Get data from database"""
    return {"Return from database_url": settings.DATABASE_URL}