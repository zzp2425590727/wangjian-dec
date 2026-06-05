from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./data/app.db"
    UPLOAD_DIR: str = "./data/uploads"
    JWT_SECRET_KEY: str = "replace-with-random-secret"
    JWT_EXPIRE_HOURS: int = 24
    BAIDU_API_KEY: str = ""
    BAIDU_SECRET_KEY: str = ""
    BAIDU_TOKEN_URL: str = "https://aip.baidubce.com/oauth/2.0/token"
    BAIDU_DETECT_URL: str = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
    BAIDU_API_TIMEOUT_SECONDS: int = 30
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_ORIGINS: str = ""  # comma-separated, e.g. "https://xxx.vercel.app,http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
