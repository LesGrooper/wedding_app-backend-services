from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os


class Settings(BaseSettings):
    load_dotenv()  # Load .env file if present
    # App
    app_name: str = os.getenv("APP_NAME")
    app_env: str = os.getenv("APP_ENV")
    secret_key: str = os.getenv("SECRET_KEY")
    qr_hmac_secret: str = os.getenv("QR_HMAC_SECRET")

    # Database
    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT"))
    db_name: str = os.getenv("DB_NAME")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    # jwt_algorithm: str = "HS256"
    jwt_algorithm: str =  os.getenv("JWT_ALGORITHM")
    jwt_expire_minutes: int = os.getenv("JWT_EXPIRE_MINUTES")

    # CORS
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
