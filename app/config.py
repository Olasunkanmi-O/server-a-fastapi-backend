from pydantic_settings import BaseSettings
from typing import Optional



class Settings(BaseSettings):        
    LLM_PROVIDER: str = "openai"
    DATABASE_URL: str
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str
    # Optional: future-proofing for other providers
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()