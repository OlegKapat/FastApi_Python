from apps.core.base_models import BaseModel
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String,text
from sqlalchemy.dialects.postgresql import ARRAY
from .constants import UserPermisionEnum


class User(BaseModel):
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=True)
    permissions: Mapped[list[str]] = mapped_column(ARRAY(String), default=lambda: [UserPermisionEnum.CAN_SELF_DELETE],
                                                   nullable=False,server_default=text("'{CAN_SELF_DELETE}'::text[]"))
