from fastapi import FastAPI
import socket

app = FastAPI(
    root_path="/api",
)
@app.get("/info")
async def get_backend():
    return ("Backend is running on host: " + socket.gethostname())