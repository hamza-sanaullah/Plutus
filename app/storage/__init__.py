"""
Plutus Backend - Storage Package
Unified storage interface for CSV operations (local and Azure Blob).

Team: Yay!
Date: August 29, 2025
"""

from .base_storage import (
    BaseStorage,
    StorageError,
    CSVValidationError,
    CSVLockError,
    validate_csv_headers,
    sanitize_csv_data,
    create_timestamp
)

from .local_storage import LocalStorage, LocalFileLock
from .azure_storage import AzureStorage, AzureBlobLease
from .storage_manager import (
    StorageManager,
    storage_manager,
    get_storage_manager,
    read_users,
    read_beneficiaries,
    read_transactions,
    read_audit_logs,
    append_user,
    append_beneficiary,
    append_transaction,
    append_audit_log
)

__all__ = [
    # Base classes
    "BaseStorage",
    "StorageError",
    "CSVValidationError", 
    "CSVLockError",
    "validate_csv_headers",
    "sanitize_csv_data",
    "create_timestamp",
    
    # Storage implementations
    "LocalStorage",
    "LocalFileLock",
    "AzureStorage",
    "AzureBlobLease",
    
    # Storage manager
    "StorageManager",
    "storage_manager",
    "get_storage_manager",
    
    # Convenience functions
    "read_users",
    "read_beneficiaries",
    "read_transactions",
    "read_audit_logs",
    "append_user",
    "append_beneficiary",
    "append_transaction",
    "append_audit_log"
]
