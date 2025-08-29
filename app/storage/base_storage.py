"""
Plutus Backend - Base Storage Interface
Abstract base class for storage operations (local and Azure).

Team: Yay!
Date: August 29, 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime


class BaseStorage(ABC):
    """
    Abstract base class for storage operations.
    Provides interface for both local and Azure Blob storage.
    """
    
    @abstractmethod
    async def read_csv(self, file_name: str) -> pd.DataFrame:
        """Read CSV file and return as DataFrame."""
        pass
    
    @abstractmethod
    async def write_csv(self, file_name: str, data: pd.DataFrame) -> bool:
        """Write DataFrame to CSV file."""
        pass
    
    @abstractmethod
    async def append_csv(self, file_name: str, data: Dict[str, Any]) -> bool:
        """Append single row to CSV file."""
        pass
    
    @abstractmethod
    async def file_exists(self, file_name: str) -> bool:
        """Check if CSV file exists."""
        pass
    
    @abstractmethod
    async def create_file_if_not_exists(self, file_name: str, headers: List[str]) -> bool:
        """Create CSV file with headers if it doesn't exist."""
        pass
    
    @abstractmethod
    async def delete_row(self, file_name: str, condition: Dict[str, Any]) -> bool:
        """Delete rows matching condition from CSV."""
        pass
    
    @abstractmethod
    async def update_row(self, file_name: str, condition: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Update rows matching condition in CSV."""
        pass
    
    @abstractmethod
    async def backup_file(self, file_name: str) -> bool:
        """Create backup of CSV file."""
        pass
    
    @abstractmethod
    async def get_file_info(self, file_name: str) -> Dict[str, Any]:
        """Get file metadata information."""
        pass


class StorageError(Exception):
    """Custom exception for storage operations."""
    
    def __init__(self, message: str, file_name: str = None, operation: str = None):
        self.message = message
        self.file_name = file_name
        self.operation = operation
        super().__init__(self.message)


class CSVValidationError(StorageError):
    """Exception for CSV validation errors."""
    pass


class CSVLockError(StorageError):
    """Exception for CSV file locking issues (concurrent access)."""
    pass


def validate_csv_headers(df: pd.DataFrame, expected_headers: List[str]) -> bool:
    """
    Validate that DataFrame has expected headers.
    """
    if df.empty:
        return True  # Empty file is valid
    
    actual_headers = list(df.columns)
    missing_headers = set(expected_headers) - set(actual_headers)
    extra_headers = set(actual_headers) - set(expected_headers)
    
    if missing_headers:
        raise CSVValidationError(f"Missing headers: {missing_headers}")
    
    if extra_headers:
        raise CSVValidationError(f"Unexpected headers: {extra_headers}")
    
    return True


def sanitize_csv_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize data for CSV storage (handle special characters, etc.).
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Replace commas, newlines, and quotes that can break CSV
            sanitized[key] = value.replace(',', '，').replace('\n', ' ').replace('\r', '')
        elif isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif value is None:
            sanitized[key] = ""
        else:
            sanitized[key] = str(value)
    
    return sanitized


def create_timestamp() -> str:
    """Create ISO timestamp for records."""
    return datetime.utcnow().isoformat() + "Z"
