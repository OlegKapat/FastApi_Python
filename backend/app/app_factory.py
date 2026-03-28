import socket
from fastapi import FastAPI
from settings import settings
from apps.info.router import info_router
from apps.users.router import router_users


def get_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, root_path="/api", )
    app.include_router(router_users, prefix="/users", tags=["users"])
    if settings.DEBUG:
       app.include_router(info_router, prefix="/info", tags=["info"])


    return app

