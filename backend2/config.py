"""Configuration via environment variables using pydantic"""
from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "glenmore"
    SECRET_KEY: str = "changeme"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "GlenmoreWellnessDB"
    APP_NAME: str = "Backend2"
    class Config:
        env_file = ".env"

settings = Settings()
