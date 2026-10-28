from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str  # postgresql+asyncpg://user:pass@endpoint:5432/shippybooks
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
