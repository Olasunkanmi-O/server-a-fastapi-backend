from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Core LLM endpoint
    LLM_ENDPOINT: str = "http://localhost:8000/infer"

    # Database
    DATABASE_URL: str

    # Optional: Plaid integration
    PLAID_CLIENT_ID: str | None = None
    PLAID_SECRET: str | None = None
    PLAID_ENV: str | None = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()