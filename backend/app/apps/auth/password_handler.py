from passlib.context import CryptContext

class PasswordEncrypt:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    async def get_password_hash(cls,password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    async def get_password_verify_hash(cls,password: str,hashed_pwd:str) -> bool:
        return cls.pwd_context.verify(password, hashed_pwd)
