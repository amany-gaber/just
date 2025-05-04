from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ROOT: str = "/api/v0"
    APP_NAME: str = "job"
    APP_DESCRIPTION: str = "job-matcher"
    DOMAIN: str = "0.0.0.0"
    BACKEND_PORT: int = 8080
    DEBUG_MODE: bool = True
