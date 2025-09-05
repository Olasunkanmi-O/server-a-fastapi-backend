from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Provider selection
    DEFAULT_PROVIDER: str
    LLM_PROVIDER: str

    # API keys
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str

    # Gemini model
    GOOGLE_MODEL: str

    # Database
    DATABASE_URL: str

    # Plaid (optional)
    PLAID_CLIENT_ID: str | None = None
    PLAID_SECRET: str | None = None
    PLAID_ENV: str | None = None

settings = Settings()