from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SkillForge Global"
    DATABASE_URL: str = "sqlite:///./app/data/skillforge.db"
    JWT_SECRET: str = "dev-secret-key-change-me"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # Admin key for protected v1 endpoints (matches X-Admin-Key header)
    ADMIN_KEY: str | None = None

    # YouTube
    YOUTUBE_API_KEY: str | None = None
    YOUTUBE_API_REGION: str = "US"

    class Config:
        env_file = ".env"

settings = Settings()
