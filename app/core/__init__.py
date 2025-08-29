"""
Plutus Backend - Core Module
Core utilities for configuration, security, and logging.

Team: Yay!
Date: August 29, 2025
"""

from .config import (
    Settings,
    AzureConfig,
    LocalConfig,
    settings,
    azure_config,
    local_config,
    get_settings,
    get_azure_config,
    get_local_config,
    is_development,
    is_production,
    get_data_storage_info
)

from .security import (
    SecurityUtils,
    security_utils,
    get_current_user,
    get_optional_user,
    get_security_utils,
    create_audit_log_entry,
    pwd_context
)

from .logging import (
    PlutusLogger,
    main_logger,
    api_logger,
    auth_logger,
    transaction_logger,
    security_logger,
    data_logger,
    get_logger,
    setup_logging,
    log_startup,
    log_shutdown,
    log_request,
    log_auth_success,
    log_auth_failure
)

__all__ = [
    # Config
    "Settings",
    "AzureConfig", 
    "LocalConfig",
    "settings",
    "azure_config",
    "local_config",
    "get_settings",
    "get_azure_config",
    "get_local_config",
    "is_development",
    "is_production",
    "get_data_storage_info",
    
    # Security
    "SecurityUtils",
    "security_utils",
    "get_current_user",
    "get_optional_user",
    "get_security_utils",
    "create_audit_log_entry",
    "pwd_context",
    
    # Logging
    "PlutusLogger",
    "main_logger",
    "api_logger",
    "auth_logger",
    "transaction_logger",
    "security_logger",
    "data_logger",
    "get_logger",
    "setup_logging",
    "log_startup",
    "log_shutdown",
    "log_request",
    "log_auth_success",
    "log_auth_failure"
]
