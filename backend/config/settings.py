import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[0]

sys.path.append(str(BASE_DIR))

from typing import Any, Dict, Optional
from urllib.parse import quote
from pydantic_settings import BaseSettings
from pydantic import BaseModel, computed_field, Field, PostgresDsn, RedisDsn
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

env_path = Path(f"{BASE_DIR}/.env")
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Weather-Forecast"
    DEBUG: bool = False
    BACKEND_CORS_ORIGINS: bool = True
    SERVER_PORT: int = 8000
    RELOAD: bool = True
    REDIS_POOL_SIZE: int = 20
    REDIS_POOL_TIMEOUT: timedelta = timedelta(seconds=30)
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6381
    REDIS_DB: int = 0
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_uri(self) -> str:
        redis_uri = RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=f"{self.REDIS_DB}",
            username=self.REDIS_USERNAME,
            password=quote(self.REDIS_PASSWORD) if self.REDIS_PASSWORD else None,
        )
        return str(redis_uri)


settings = Settings()
