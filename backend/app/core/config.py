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
    
    # Zoom Integration
    ZOOM_API_KEY: str | None = None
    ZOOM_API_SECRET: str | None = None
    
    # Stripe Payment
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
