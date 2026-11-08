from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///data.db"
    environment: str = "development"
    persistent_memory: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
