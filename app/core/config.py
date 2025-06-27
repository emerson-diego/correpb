import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Corre PB API"
    PROJECT_DESCRIPTION: str = "API para eventos de corrida na Paraíba"
    VERSION: str = "0.1.0"

    API_V1_STR: str = "/api/v1"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8181"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "True").lower() == "true"

    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "correpb")

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://correpbfrontend.vercel.app"
    ]

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    SCRAPER_DELAY: float = float(os.getenv("SCRAPER_DELAY", "1.0"))

    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_EXPIRE: int = int(os.getenv("CACHE_EXPIRE", "3600"))  # 1 hora em segundos

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()