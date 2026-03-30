import socket
from fastapi import APIRouter
from settings import settings
from .schemas import BaseBackendInfoSchema, DatabaseInfoSchema
import logging

info_router = APIRouter()


@info_router.get("/backend")
async def get_backend() -> BaseBackendInfoSchema:
    """Get data from backend"""
    logging.error(
        "some info",
        extra={
            "user_id": 123,
            "debug_info": {"function": "get_backend_info", "status": "OK"},
        },
    )
    return BaseBackendInfoSchema(backend=socket.gethostname())


@info_router.get("/database")
async def get_database() -> DatabaseInfoSchema:
    """Get data from database"""
    return DatabaseInfoSchema(database_url=settings.DATABASE_ASYNC_URL)
