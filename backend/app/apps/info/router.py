import socket
from fastapi import APIRouter
from settings import settings
from .schemas import BaseBackendInfoSchema,DatabaseInfoSchema

info_router = APIRouter()



@info_router.get("/backend")
async def get_backend()->BaseBackendInfoSchema:
    """Get data from backend"""
    return BaseBackendInfoSchema(backend=socket.gethostname())

@info_router.get("/database")
async def get_database()->DatabaseInfoSchema:
    """Get data from database"""
    return DatabaseInfoSchema(database_url=settings.DATABASE_ASYNC_URL)