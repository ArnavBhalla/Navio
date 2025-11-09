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
