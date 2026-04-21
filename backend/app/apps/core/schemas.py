from pydantic import BaseModel, Field


class IdSchema(BaseModel):
    id: int = Field(description="Unique identifier", gt=0)


class InstanceVersion(BaseModel):
    version: int = Field(examples=[1, 2], gt=0)
