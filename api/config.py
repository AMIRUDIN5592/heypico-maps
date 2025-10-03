from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_ENV: str = Field("production", description="App environment")
    TZ: str = Field("Asia/Jakarta", description="Timezone")

    # API base URL for generating absolute links in chat responses
    API_BASE_URL: str = Field("http://localhost:8000", description="Public base URL for this API")

    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    # Google Maps (must be provided via .env; keep default empty to avoid leaking)
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_MAPS_BASE_URL: str = "https://maps.googleapis.com/maps/api"

    # Rate limit
    RATE_LIMIT_PER_MINUTE: int = 60
    REDIS_URL: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
