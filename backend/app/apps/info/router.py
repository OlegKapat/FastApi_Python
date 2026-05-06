import logging
import socket
from asyncio import sleep
from uuid import uuid4

from apps.services.redis_service import redis_service
from apps.storage.s3 import s3_storage
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi_cache.decorator import cache
from settings import settings

from .schemas import BaseBackendInfoSchema, DatabaseInfoSchema, RedisHealthSchema

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


@info_router.get("/heavy-endpoint")
@cache(expire=30, namespace="params")
async def get_heavy_endpoint(some_params: int) -> dict:
    await sleep(5)  # Simulate a heavy operation
    return {"message": f"Heavy operation completed with params: {some_params * 2}"}


@info_router.post("/upload-file")
async def upload_file(files: UploadFile = File(...)) -> dict:
    uuid_id = uuid4()
    urls = await s3_storage.upload_file_to_s3(files, uuid_id)
    return {"urls": urls}
