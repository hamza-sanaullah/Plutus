"""
Plutus Backend - Storage Manager
Unified interface that switches between local and Azure storage based on configuration.

Team: Yay!
Date: August 29, 2025
"""

from typing import List, Dict, Any, Optional
import pandas as pd

from .base_storage import BaseStorage, StorageError
from .local_storage import LocalStorage
from .azure_storage import AzureStorage
from ..core.config import get_settings
from ..core.logging import data_logger


class StorageManager:
    """
    Unified storage manager that automatically switches between local and Azure storage
    based on configuration settings.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._storage: Optional[BaseStorage] = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize the appropriate storage backend."""
        try:
            if self.settings.use_local_storage:
                self._storage = LocalStorage()
                data_logger.info("🗂️ Initialized Local Storage for CSV operations")
            else:
                self._storage = AzureStorage()
                data_logger.info("☁️ Initialized Azure Blob Storage for CSV operations")
                
        except Exception as e:
            data_logger.error(f"❌ Failed to initialize storage: {str(e)}")
            # Fallback to local storage
            try:
                self._storage = LocalStorage()
                data_logger.warning("⚠️ Falling back to Local Storage")
            except Exception as fallback_error:
                raise StorageError(f"Failed to initialize any storage backend: {str(fallback_error)}")
    
    @property
    def storage_type(self) -> str:
        """Get current storage type."""
        if isinstance(self._storage, LocalStorage):
            return "local"
        elif isinstance(self._storage, AzureStorage):
            return "azure"
        return "unknown"
    
    async def read_csv(self, file_name: str) -> pd.DataFrame:
        """Read CSV file and return as DataFrame."""
        return await self._storage.read_csv(file_name)
    
    async def write_csv(self, file_name: str, data: pd.DataFrame) -> bool:
        """Write DataFrame to CSV file."""
        return await self._storage.write_csv(file_name, data)
    
    async def append_csv(self, file_name: str, data: Dict[str, Any]) -> bool:
        """Append single row to CSV file."""
        return await self._storage.append_csv(file_name, data)
    
    async def file_exists(self, file_name: str) -> bool:
        """Check if CSV file exists."""
        return await self._storage.file_exists(file_name)
    
    async def create_file_if_not_exists(self, file_name: str, headers: List[str]) -> bool:
        """Create CSV file with headers if it doesn't exist."""
        return await self._storage.create_file_if_not_exists(file_name, headers)
    
    async def delete_row(self, file_name: str, condition: Dict[str, Any]) -> bool:
        """Delete rows matching condition from CSV."""
        return await self._storage.delete_row(file_name, condition)
    
    async def update_row(self, file_name: str, condition: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Update rows matching condition in CSV."""
        return await self._storage.update_row(file_name, condition, updates)
    
    async def backup_file(self, file_name: str) -> bool:
        """Create backup of CSV file."""
        return await self._storage.backup_file(file_name)
    
    async def get_file_info(self, file_name: str) -> Dict[str, Any]:
        """Get file metadata information."""
        return await self._storage.get_file_info(file_name)
    
    async def initialize_csv_files(self) -> bool:
        """Initialize all required CSV files with proper headers."""
        csv_schemas = {
            self.settings.users_csv: [
                "user_id", "username", "hashed_password", "account_number", 
                "balance", "daily_limit", "created_at"
            ],
            self.settings.beneficiaries_csv: [
                "owner_user_id", "beneficiary_id", "name", "bank_name", 
                "account_number", "added_at"
            ],
            self.settings.transactions_csv: [
                "transaction_id", "from_user_id", "to_user_id", "from_account", 
                "to_account", "amount", "status", "description", "timestamp", "daily_total_sent"
            ],
            self.settings.audit_logs_csv: [
                "log_id", "user_id", "action", "details", "timestamp", 
                "ip_address", "request_id"
            ]
        }
        
        success_count = 0
        for file_name, headers in csv_schemas.items():
            try:
                created = await self.create_file_if_not_exists(file_name, headers)
                if created:
                    data_logger.info(f"✅ Created CSV file: {file_name}")
                    success_count += 1
                else:
                    data_logger.info(f"📄 CSV file already exists: {file_name}")
                    
            except Exception as e:
                data_logger.error(f"❌ Failed to initialize {file_name}: {str(e)}")
                return False
        
        if success_count > 0:
            data_logger.info(f"🎯 Initialized {success_count} new CSV files")
        
        return True
    
    async def get_storage_health(self) -> Dict[str, Any]:
        """Get storage system health information."""
        try:
            health_info = {
                "storage_type": self.storage_type,
                "status": "healthy",
                "files": {}
            }
            
            # Check all CSV files
            csv_files = [
                self.settings.users_csv,
                self.settings.beneficiaries_csv,
                self.settings.transactions_csv,
                self.settings.audit_logs_csv
            ]
            
            for file_name in csv_files:
                try:
                    file_info = await self.get_file_info(file_name)
                    health_info["files"][file_name] = {
                        "exists": file_info.get("exists", False),
                        "rows": file_info.get("rows", 0),
                        "size_bytes": file_info.get("size_bytes", 0),
                        "status": "healthy"
                    }
                except Exception as e:
                    health_info["files"][file_name] = {
                        "exists": False,
                        "status": "error",
                        "error": str(e)
                    }
                    health_info["status"] = "degraded"
            
            return health_info
            
        except Exception as e:
            return {
                "storage_type": self.storage_type,
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def migrate_to_azure(self, azure_connection_string: str) -> bool:
        """Migrate data from local storage to Azure Blob Storage."""
        if not isinstance(self._storage, LocalStorage):
            raise StorageError("Migration only supported from local storage")
        
        try:
            # Temporarily switch to Azure for migration
            original_setting = self.settings.use_local_storage
            self.settings.azure_storage_connection_string = azure_connection_string
            self.settings.use_local_storage = False
            
            azure_storage = AzureStorage()
            
            # Get all CSV files from local storage
            csv_files = [
                self.settings.users_csv,
                self.settings.beneficiaries_csv,
                self.settings.transactions_csv,
                self.settings.audit_logs_csv
            ]
            
            migrated_count = 0
            for file_name in csv_files:
                if await self._storage.file_exists(file_name):
                    # Read from local
                    df = await self._storage.read_csv(file_name)
                    
                    # Write to Azure
                    await azure_storage.write_csv(file_name, df)
                    
                    data_logger.info(f"📤 Migrated {file_name} to Azure ({len(df)} rows)")
                    migrated_count += 1
            
            data_logger.info(f"🎯 Successfully migrated {migrated_count} files to Azure")
            
            # Switch to Azure storage
            self._storage = azure_storage
            
            return True
            
        except Exception as e:
            # Restore original setting on failure
            self.settings.use_local_storage = original_setting
            data_logger.error(f"❌ Migration to Azure failed: {str(e)}")
            return False


# Global storage manager instance
storage_manager = StorageManager()


def get_storage_manager() -> StorageManager:
    """
    Dependency to get storage manager instance.
    """
    return storage_manager


# Convenience functions for common operations
async def read_users() -> pd.DataFrame:
    """Read users CSV file."""
    return await storage_manager.read_csv(storage_manager.settings.users_csv)


async def read_beneficiaries() -> pd.DataFrame:
    """Read beneficiaries CSV file."""
    return await storage_manager.read_csv(storage_manager.settings.beneficiaries_csv)


async def read_transactions() -> pd.DataFrame:
    """Read transactions CSV file."""
    return await storage_manager.read_csv(storage_manager.settings.transactions_csv)


async def read_audit_logs() -> pd.DataFrame:
    """Read audit logs CSV file."""
    return await storage_manager.read_csv(storage_manager.settings.audit_logs_csv)


async def append_user(user_data: Dict[str, Any]) -> bool:
    """Append new user to users CSV."""
    return await storage_manager.append_csv(storage_manager.settings.users_csv, user_data)


async def append_beneficiary(beneficiary_data: Dict[str, Any]) -> bool:
    """Append new beneficiary to beneficiaries CSV."""
    return await storage_manager.append_csv(storage_manager.settings.beneficiaries_csv, beneficiary_data)


async def append_transaction(transaction_data: Dict[str, Any]) -> bool:
    """Append new transaction to transactions CSV."""
    return await storage_manager.append_csv(storage_manager.settings.transactions_csv, transaction_data)


async def append_audit_log(audit_data: Dict[str, Any]) -> bool:
    """Append new audit log to audit logs CSV."""
    return await storage_manager.append_csv(storage_manager.settings.audit_logs_csv, audit_data)
