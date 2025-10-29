from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SkillForge Global"
    DATABASE_URL: str = "sqlite:///./app/data/skillforge.db"
    JWT_SECRET: str = "dev-secret-key-change-me"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
