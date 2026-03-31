from functools import lru_cache
from pydantic_settings import BaseSettings


class CoreSettings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    DEBUG: bool = True

class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES:int = 5
    JWT_REFRESH_TOKEN_EXPIRES: int = 60


class PostgresSettings(BaseSettings):
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PORT: int = 5432
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 1800

    @property
    def DATABASE_ASYNC_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PORT}/{self.PGDATABASE}"


class Settings(CoreSettings, PostgresSettings, JWTSettings):
    SENTRY_DSN: str


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
