from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "GlenmoreWellnessDB"
    APP_NAME: str = "Backend2"
    class Config:
        env_file = ".env"

settings = Settings()
