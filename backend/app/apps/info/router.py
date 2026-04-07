import socket
from fastapi import APIRouter, HTTPException
from settings import settings
from apps.services.redis_service import redis_service
from .schemas import BaseBackendInfoSchema, DatabaseInfoSchema, RedisHealthSchema
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


@info_router.get("/redis")
async def get_redis_health() -> RedisHealthSchema:
    """Check Redis availability."""
    is_healthy, detail = await redis_service.health_check()
    if not is_healthy:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {detail}")
    return RedisHealthSchema(status="ok", healthy=True)

