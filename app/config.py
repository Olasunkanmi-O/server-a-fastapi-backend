from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DEFAULT_PROVIDER: str
    LLM_PROVIDER: str
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    GOOGLE_MODEL: str
    DATABASE_URL: str
    PLAID_CLIENT_ID: str | None = None
    PLAID_SECRET: str | None = None
    PLAID_ENV: str | None = None

settings = Settings()  # ✅ This must be present and used everywhere
