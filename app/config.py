from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application settings
    app_name: str = "SOAREngine"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Threat Intelligence API Keys
    abuseipdb_api_key: Optional[str] = None
    virustotal_api_key: Optional[str] = None
    
    # Slack Integration
    slack_webhook_url: Optional[str] = None
    slack_default_channel: str = "#security-alerts"
    
    # Ticketing Integration
    ticketing_enabled: bool = False
    ticketing_api_url: Optional[str] = None
    ticketing_api_key: Optional[str] = None
    
    # Playbook settings
    playbook_auto_run: bool = True
    playbook_max_concurrent: int = 5
    
    # Enrichment settings
    enrichment_timeout: int = 10
    enrichment_cache_ttl: int = 3600
    
    # Metrics settings
    metrics_enabled: bool = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()