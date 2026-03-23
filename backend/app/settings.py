from functools import lru_cache
from pydantic_settings import BaseSettings

class CoreSettings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    DEBUG: bool = False

class Settings(CoreSettings):
    pass

@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()