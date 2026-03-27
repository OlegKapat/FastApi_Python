

from apps.core.base_crud import BaseCrudManagerl
from .models import User
from .schemas import RegisteredUserSchema, UserRegistrationSchema
from sqlalchemy.ext.asyncio import AsyncSession
from apps.auth.password_handler import PasswordEncrypt


class UserCrudManager(BaseCrudManagerl):
    def __init__(self):
        self.model = User

    async def create_user(self, new_user: RegisteredUserSchema, session: AsyncSession)->User:
        hashed_password = await PasswordEncrypt.get_password_hash(new_user.password)
        return await self.create_instance(
            session=session,
            email=new_user.email,
            hashed_password=hashed_password,
            name=new_user.name,
        )

user_manager = UserCrudManager()