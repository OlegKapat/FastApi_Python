import socket
from fastapi import FastAPI
from settings import settings


def get_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, root_path="/api", )

    @app.get("/info")
    async def get_backend():
        return {"Return from backend": socket.gethostname()}

    return app
