"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )
    
    # Application
    app_name: str = "LuminaMed-AI"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Security
    secret_key: str = "dev-secret-key"
    algorithm: str = "HS256"
    
    # Cache
    redis_url: str = "redis://localhost:6379/0"
    
    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection: str = "radiology_knowledge"
    
    # Model
    model_provider: str = "google"
    google_api_key: Optional[str] = None
    model_name: str = "gemini-2.0-flash-exp"
    model_temperature: float = 0.1
    max_tokens: int = 8192
    
    # Medical AI
    use_multimodal: bool = True
    enable_verification: bool = True
    hallucination_threshold: float = 0.15
    confidence_threshold: float = 0.70
    
    # Upload
    max_upload_bytes: int = 52428800
    allowed_content_types: str = "image/png,image/jpeg,application/dicom"
    
    @property
    def allowed_content_types_list(self) -> list[str]:
        """Parse allowed content types."""
        return [ct.strip() for ct in self.allowed_content_types.split(",")]


# Singleton pattern
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (cached)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings