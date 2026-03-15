from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    app_name: str = "TelegramOpenRouterBot"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    telegram_bot_token: SecretStr
    telegram_webhook_secret: SecretStr
    telegram_webhook_url: str
    
    openrouter_api_key: SecretStr
    openrouter_model_default: str = "openai/gpt-3.5-turbo"
    openrouter_model_code: str = "anthropic/claude-3-haiku"
    openrouter_model_research: str = "perplexity/sonar-small-chat"
    openrouter_site_url: str = ""
    openrouter_app_name: str = "TelegramOpenRouterBot"
    
    database_url: str
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
