from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SkillForge Global"
    DATABASE_URL: str = "sqlite:///./app/data/skillforge.db"
    JWT_SECRET: str = "dev-secret-key-change-me"
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    
    # Debug / Logging
    DEBUG: bool = True  # Include verbose error details in responses (dev only)

    # Admin key for protected v1 endpoints (matches X-Admin-Key header)
    ADMIN_KEY: str | None = None

    # YouTube
    YOUTUBE_API_KEY: str | None = None
    YOUTUBE_API_REGION: str = "US"
    
    # LLM Provider for AI Quiz Generation
    AI_PROVIDER: str = "openai"  # Options: openai, anthropic, azure, ollama
    # Test keys for development - REPLACE IN PRODUCTION
    OPENAI_API_KEY: str = "sk-test-key-replace-in-production-with-real-openai-key"
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = "sk-ant-test-key-replace-in-production-with-real-anthropic-key"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_DEPLOYMENT: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
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
