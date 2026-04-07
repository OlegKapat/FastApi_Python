from pydantic import BaseModel, Field


class BaseBackendInfoSchema(BaseModel):
    backend: str = Field(examples=["backend1", "backend2"])

class DatabaseInfoSchema(BaseModel):
    database_url: str


class RedisHealthSchema(BaseModel):
    status: str = Field(examples=["ok", "down"])
    healthy: bool
    detail: str | None = None

