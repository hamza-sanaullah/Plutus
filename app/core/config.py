"""
Plutus Backend - Core Configuration Settings
Manages application settings, environment variables, and Azure configurations.

Team: Yay!
Date: August 29, 2025
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Application Settings
    app_name: str = "Plutus Banking Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security Settings
    secret_key: str = "plutus-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Settings
    allowed_origins: List[str] = ["*"]  # Configure for production
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    # Azure Blob Storage Configuration
    azure_storage_connection_string: Optional[str] = None
    azure_storage_account_name: Optional[str] = None
    azure_storage_account_key: Optional[str] = None
    azure_container_name: str = "plutus-data"
    
    # Local Development Settings
    use_local_storage: bool = True  # Set to False when using Azure
    local_data_path: str = "data"
    
    # CSV File Names
    users_csv: str = "users.csv"
    transactions_csv: str = "transactions.csv"
    beneficiaries_csv: str = "beneficiaries.csv"
    audit_logs_csv: str = "audit_logs.csv"
    
    # Banking Business Rules
    default_starting_balance: float = 1000.0
    default_daily_limit: float = 10000.0
    daily_transfer_limit: float = 50000.0
    daily_transaction_limit: int = 10
    max_transaction_amount: float = 50000.0
    min_transaction_amount: float = 1.0
    
    # Transaction Settings
    transaction_statuses: List[str] = ["pending", "success", "failed"]
    supported_currencies: List[str] = ["PKR", "USD"]
    default_currency: str = "PKR"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_audit_logging: bool = True
    
    # Rate Limiting
    max_requests_per_minute: int = 100
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # File Upload Settings
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = [".csv", ".pdf"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class AzureConfig:
    """
    Azure Blob Storage specific configurations and utilities.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
    @property
    def connection_string(self) -> Optional[str]:
        """Get Azure Storage connection string."""
        return self.settings.azure_storage_connection_string
    
    @property
    def is_azure_enabled(self) -> bool:
        """Check if Azure Blob Storage is properly configured."""
        return (
            not self.settings.use_local_storage and
            self.connection_string is not None
        )
    
    @property
    def container_name(self) -> str:
        """Get Azure container name."""
        return self.settings.azure_container_name
    
    def get_blob_name(self, csv_file: str) -> str:
        """Generate blob name for CSV file."""
        return f"plutus-data/{csv_file}"


class LocalConfig:
    """
    Local file system configurations for development.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.data_path = Path(settings.local_data_path)
        
    def ensure_data_directory(self) -> None:
        """Ensure local data directory exists."""
        self.data_path.mkdir(exist_ok=True)
        
    def get_csv_path(self, csv_file: str) -> Path:
        """Get full path for CSV file."""
        return self.data_path / csv_file
    
    @property
    def is_local_enabled(self) -> bool:
        """Check if local storage is enabled."""
        return self.settings.use_local_storage


# Global settings instance
settings = Settings()

# Configuration instances
azure_config = AzureConfig(settings)
local_config = LocalConfig(settings)


def get_settings() -> Settings:
    """
    Dependency to get settings instance.
    """
    return settings


def get_azure_config() -> AzureConfig:
    """
    Dependency to get Azure configuration.
    """
    return azure_config


def get_local_config() -> LocalConfig:
    """
    Dependency to get local configuration.
    """
    return local_config


# Development helper functions
def is_development() -> bool:
    """Check if running in development mode."""
    return settings.environment == "development"


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.environment == "production"


def get_data_storage_info() -> dict:
    """Get information about current data storage configuration."""
    return {
        "storage_type": "local" if settings.use_local_storage else "azure",
        "azure_enabled": azure_config.is_azure_enabled,
        "local_enabled": local_config.is_local_enabled,
        "container_name": settings.azure_container_name,
        "local_data_path": settings.local_data_path
    }
