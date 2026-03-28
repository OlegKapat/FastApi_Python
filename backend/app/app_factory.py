import socket
from fastapi import FastAPI,Request
from settings import settings
from apps.info.router import info_router
from apps.users.router import router_users
from scalar_fastapi import get_scalar_api_reference


def get_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, root_path="/api", )
    app.include_router(router_users, prefix="/users", tags=["users"])
    if settings.DEBUG:
        app.include_router(info_router, prefix="/info", tags=["info"])

    @app.get("/scalar", include_in_schema=False)
    async def scalar_html(request: Request):
        return get_scalar_api_reference(
            # Your OpenAPI document
            openapi_url= request.scope.get("root_path","") + app.openapi_url,
            # Avoid CORS issues (optional)
            scalar_proxy_url="https://proxy.scalar.com",
        )

    return app
