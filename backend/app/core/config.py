from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # AI Models
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Scraping
    FIRECRAWL_API_KEY: Optional[str] = None

    # App Config
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"

    # Auth / JWT
    AUTH_SECRET_KEY: str = "change-me-in-production"
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Demo users (for JWT auth)
    DEMO_ADMIN_USERNAME: str = "admin"
    DEMO_ADMIN_PASSWORD: str = "admin123"  # For demo only – override via .env
    DEMO_USER_USERNAME: str = "demo"
    DEMO_USER_PASSWORD: str = "demo123"  # For demo only – override via .env

    # Model Config
    OPENAI_MODEL: str = "gpt-4o"  # Will swap to gpt-5 when available
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # RAG Config
    RETRIEVAL_K: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
