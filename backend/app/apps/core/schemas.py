
from pydantic import BaseModel, Field



class IdSchema(BaseModel):
    id: int = Field(description="Unique identifier",gt=0)
