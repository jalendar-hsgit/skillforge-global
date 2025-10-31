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
    
    # Email Configuration
    EMAIL_PROVIDER: str = "smtp"  # Options: smtp, sendgrid, ses
    EMAIL_FROM: str = "noreply@skillforge.global"
    EMAIL_FROM_NAME: str = "SkillForge Global"
    
    # SMTP Settings (for EMAIL_PROVIDER=smtp)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    
    # SendGrid (for EMAIL_PROVIDER=sendgrid)
    SENDGRID_API_KEY: str | None = None
    
    # AWS SES (for EMAIL_PROVIDER=ses)
    AWS_REGION: str = "us-east-1"

    class Config:
        env_file = ".env"

settings = Settings()
