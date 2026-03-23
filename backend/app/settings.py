from functools import lru_cache
from pydantic_settings import BaseSettings


class CoreSettings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    DEBUG: bool = True


class PostgresSettings(BaseSettings):
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PORT}/{self.PGDATABASE}"


class Settings(CoreSettings, PostgresSettings):
    pass


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
