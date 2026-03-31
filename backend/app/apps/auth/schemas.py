from pydantic import BaseModel

class LoginResposeSchema(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = 'Bearer'

