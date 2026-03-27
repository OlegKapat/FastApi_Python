from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from password_strength import PasswordPolicy
from apps.core.schemas import IdSchema

password_policy = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    special=1,
)


class UserPasswordSchema(BaseModel):
    password: str = Field(description="Password", examples=["!jsK23oipl"])

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        try:
            errors = password_policy.test(value)
            if not errors:
                return value
            error_msg = []
            for error in errors:
                if error.name() == 'length':
                    error_msg.append("Password must be at least 8 characters long.")
                elif error.name() == 'uppercase':
                    error_msg.append("Password must contain at least one uppercase letter.")
                elif error.name() == 'numbers':
                    error_msg.append("Password must contain at least one number.")
                elif error.name() == 'special':
                    error_msg.append("Password must contain at least one special character.")
            raise ValueError(" ".join(error_msg))
        except Exception as e:
            raise ValueError(f"Password does not meet the policy requirements: {str(e)}")


class BaseUserSchema(BaseModel):
    name: Annotated[str, StringConstraints(pattern=r"^[0-9a-zA-Zа-яА-ЯїЇяЯєЄіІґҐ_.'\- ]+$",
                                           strip_whitespace=True,
                                           max_length=50,
                                           min_length=3)] = Field(description="Name",
                                                                      examples=["John Doe", "Jane Smith"])
    email: EmailStr = Field(description="User email", examples=["bomb@ukr.net"])


class UserRegistrationSchema(BaseUserSchema, UserPasswordSchema):
    pass


class RegisteredUserSchema(BaseUserSchema, IdSchema,UserPasswordSchema):
    pass

class ResponseUserSchema(BaseUserSchema, IdSchema):
    pass