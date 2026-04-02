from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from apps.users.crud import user_manager
from apps.users.models import User
from .schemas import LoginResposeSchema
from .password_handler import PasswordEncrypt
from datetime import datetime, timedelta
from uuid import uuid4
import jwt


class AuthHandler:
    def __init__(self):
        self.access_token = settings.JWT_ACCESS_TOKEN_EXPIRES
        self.refresh_token = settings.JWT_REFRESH_TOKEN_EXPIRES
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.jwr_secret_key = settings.JWT_SECRET_KEY

    async def get_login_token(self, session: AsyncSession, request: OAuth2PasswordRequestForm) -> LoginResposeSchema:
        user: User | None = await user_manager.get(
            session=session,
            field_value=request.username,
            field=User.email,
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")

        is_valid_password = await PasswordEncrypt.get_password_verify_hash(request.password, user.hashed_password)
        if not is_valid_password:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")
        token_response = await self.generate_tokens(user)
        return token_response

    async def generate_tokens(self, user: User) -> LoginResposeSchema:
        access_token_payload = {
            "sub": str(user.id),
            "email": user.email,

        }
        access_token = await  self.generate_token(payload=access_token_payload, expire_minutes=self.access_token)
        refresh_token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "key": uuid4().hex

        }
        refresh_token = await  self.generate_token(payload=refresh_token_payload, expire_minutes=self.refresh_token)
        return LoginResposeSchema(access_token=access_token, refresh_token=refresh_token,
                                  expires_in=self.access_token * 60,
                                  token_type="Bearer")

    async def generate_token(self, payload: dict, expire_minutes: int) -> str:
        expire = datetime.now() + timedelta(minutes=expire_minutes)
        payload.update({"exp": expire})
        token = jwt.encode(payload, self.jwr_secret_key, algorithm=self.jwt_algorithm)
        return token

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.jwr_secret_key, algorithms=self.jwt_algorithm)
            payload["iat"] = datetime.fromtimestamp(payload["iat"])
            payload["exp"] = datetime.fromtimestamp(payload["exp"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")


auth_handler = AuthHandler()
