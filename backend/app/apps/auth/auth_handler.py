from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from apps.users.crud import user_manager
from apps.users.models import User
from .schemas import LoginResposeSchema
from .password_handler import PasswordEncrypt


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

        return LoginResposeSchema(access_token="sASadAD", refresh_token="SADAD", expires_in=10, token_type="Bearer")


auth_handler = AuthHandler()
