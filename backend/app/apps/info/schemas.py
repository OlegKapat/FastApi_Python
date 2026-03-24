from pydantic import BaseModel, Field


class BaseBackendInfoSchema(BaseModel):
    backend: str = Field(examples=["backend1", "backend2"])

class DatabaseInfoSchema(BaseModel):
    database_url: str
