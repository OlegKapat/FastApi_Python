from fastapi import FastAPI, Request
from settings import settings
from apps.info.router import info_router
from apps.users.router import router_users
from apps.auth.router import router_auth
from scalar_fastapi import get_scalar_api_reference
from fastapi.responses import JSONResponse
from apps.services.sentry_service import init_sentry
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi import FastAPI
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from apps.services.redis_service import redis_service

init_sentry()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis = redis_service.get_redis_client
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()
    await redis.connection_pool.disconnect()


def get_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, root_path="/api", default_response_class=JSONResponse,
                  lifespan=lifespan)
    app.include_router(router_users, prefix="/users", tags=["users"])
    app.include_router(router_auth, prefix="/auth", tags=["auth"])
    if settings.DEBUG:
        app.include_router(info_router, prefix="/info", tags=["info"])

    @app.get("/scalar", include_in_schema=False)
    async def scalar_html(request: Request):
        return get_scalar_api_reference(
            # Your OpenAPI document
            openapi_url=request.scope.get("root_path", "") + app.openapi_url,
            # Avoid CORS issues (optional)
            scalar_proxy_url="https://proxy.scalar.com",
        )

    return app
