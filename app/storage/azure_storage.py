"""
Plutus Backend - Azure Blob Storage Implementation
Handles CSV operations with Azure Blob Storage for production.

Team: Yay!
Date: August 29, 2025
"""

import pandas as pd
import asyncio
from typing import List, Dict, Any, Optional
from io import StringIO, BytesIO
from datetime import datetime, timedelta
import uuid

try:
    from azure.storage.blob.aio import BlobServiceClient
    from azure.storage.blob import generate_blob_sas, BlobSasPermissions
    from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from .base_storage import BaseStorage, StorageError, CSVValidationError
from .base_storage import validate_csv_headers, sanitize_csv_data, create_timestamp
from ..core.config import get_azure_config
from ..core.logging import data_logger


class AzureStorage(BaseStorage):
    """
    Azure Blob Storage implementation for CSV operations.
    Handles blob operations, concurrent access, and data validation.
    """
    
    def __init__(self):
        if not AZURE_AVAILABLE:
            raise StorageError("Azure Storage SDK not available. Install azure-storage-blob package.")
        
        self.config = get_azure_config()
        self.client: Optional[BlobServiceClient] = None
        self.lock_timeout = 30  # seconds
        
        if not self.config.is_azure_enabled:
            raise StorageError("Azure Blob Storage not properly configured")
    
    async def _get_client(self) -> BlobServiceClient:
        """Get or create Azure Blob Service Client."""
        if self.client is None:
            self.client = BlobServiceClient.from_connection_string(
                self.config.connection_string
            )
        return self.client
    
    async def _ensure_container_exists(self):
        """Ensure the container exists."""
        try:
            client = await self._get_client()
            container_client = client.get_container_client(self.config.container_name)
            await container_client.create_container()
        except ResourceExistsError:
            pass  # Container already exists
        except Exception as e:
            raise StorageError(f"Failed to ensure container exists: {str(e)}")
    
    def _get_blob_name(self, file_name: str) -> str:
        """Get blob name for CSV file."""
        return self.config.get_blob_name(file_name)
    
    async def read_csv(self, file_name: str) -> pd.DataFrame:
        """Read CSV file from blob and return as DataFrame."""
        blob_name = self._get_blob_name(file_name)
        
        try:
            await self._ensure_container_exists()
            client = await self._get_client()
            blob_client = client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )
            
            # Check if blob exists
            if not await self.file_exists(file_name):
                data_logger.log_data_operation(
                    "read", file_name, False,
                    error_details="Blob not found"
                )
                return pd.DataFrame()
            
            # Download blob content
            download_stream = await blob_client.download_blob()
            content = await download_stream.readall()
            
            # Parse CSV
            csv_string = content.decode('utf-8')
            df = pd.read_csv(StringIO(csv_string))
            
            data_logger.log_data_operation(
                "read", file_name, True,
                error_details=f"Read {len(df)} rows from blob"
            )
            
            return df
            
        except Exception as e:
            data_logger.log_data_operation(
                "read", file_name, False,
                error_details=str(e)
            )
            raise StorageError(f"Failed to read CSV from blob: {str(e)}", file_name, "read")
    
    async def write_csv(self, file_name: str, data: pd.DataFrame) -> bool:
        """Write DataFrame to CSV blob."""
        blob_name = self._get_blob_name(file_name)
        
        try:
            await self._ensure_container_exists()
            
            # Create backup before writing
            if await self.file_exists(file_name):
                await self.backup_file(file_name)
            
            # Convert DataFrame to CSV string
            csv_buffer = StringIO()
            data.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            # Upload to blob with lease for atomic operation
            async with self._blob_lease(file_name) as blob_client:
                await blob_client.upload_blob(
                    csv_content.encode('utf-8'),
                    overwrite=True,
                    content_type="text/csv"
                )
            
            data_logger.log_data_operation(
                "write", file_name, True,
                error_details=f"Wrote {len(data)} rows to blob"
            )
            
            return True
            
        except Exception as e:
            data_logger.log_data_operation(
                "write", file_name, False,
                error_details=str(e)
            )
            raise StorageError(f"Failed to write CSV to blob: {str(e)}", file_name, "write")
    
    async def append_csv(self, file_name: str, data: Dict[str, Any]) -> bool:
        """Append single row to CSV blob."""
        try:
            # Sanitize data
            sanitized_data = sanitize_csv_data(data)
            
            # Read existing data
            df = await self.read_csv(file_name)
            
            # Create new row
            new_row = pd.DataFrame([sanitized_data])
            
            # Append and write back
            if df.empty:
                updated_df = new_row
            else:
                updated_df = pd.concat([df, new_row], ignore_index=True)
            
            success = await self.write_csv(file_name, updated_df)
            
            if success:
                data_logger.log_data_operation(
                    "append", file_name, True,
                    error_details=f"Appended 1 row to blob"
                )
            
            return success
            
        except Exception as e:
            data_logger.log_data_operation(
                "append", file_name, False,
                error_details=str(e)
            )
            raise StorageError(f"Failed to append to CSV blob: {str(e)}", file_name, "append")
    
    async def file_exists(self, file_name: str) -> bool:
        """Check if CSV blob exists."""
        blob_name = self._get_blob_name(file_name)
        
        try:
            client = await self._get_client()
            blob_client = client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )
            
            return await blob_client.exists()
            
        except Exception:
            return False
    
    async def create_file_if_not_exists(self, file_name: str, headers: List[str]) -> bool:
        """Create CSV blob with headers if it doesn't exist."""
        try:
            if not await self.file_exists(file_name):
                # Create empty DataFrame with headers
                df = pd.DataFrame(columns=headers)
                await self.write_csv(file_name, df)
                
                data_logger.log_data_operation(
                    "create", file_name, True,
                    error_details=f"Created blob with headers: {headers}"
                )
                
                return True
            
            return False  # Blob already exists
            
        except Exception as e:
            data_logger.log_data_operation(
                "create", file_name, False,
                error_details=str(e)
            )
            raise StorageError(f"Failed to create CSV blob: {str(e)}", file_name, "create")
    
    async def delete_row(self, file_name: str, condition: Dict[str, Any]) -> bool:
        """Delete rows matching condition from CSV blob."""
        try:
            df = await self.read_csv(file_name)
            
            if df.empty:
                return False
            
            # Build condition mask
            mask = pd.Series([True] * len(df))
            for column, value in condition.items():
                if column in df.columns:
                    mask = mask & (df[column] == value)
                else:
                    raise CSVValidationError(f"Column '{column}' not found in CSV")
            
            # Count rows to delete
            rows_to_delete = mask.sum()
            
            if rows_to_delete == 0:
                return False
            
            # Remove matching rows
            df_filtered = df[~mask]
            
            # Write back
            await self.write_csv(file_name, df_filtered)
            
            data_logger.log_data_operation(
                "delete", file_name, True,
                error_details=f"Deleted {rows_to_delete} rows from blob"
            )
            
            return True
            
        except Exception as e:
            data_logger.log_data_operation(
                "delete", file_name, False,
                error_details=str(e)
            )
            raise StorageError(f"Failed to delete from CSV blob: {str(e)}", file_name, "delete")
    
    async def update_row(self, file_name: str, condition: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Update rows matching condition in CSV blob."""
        try:
            df = await self.read_csv(file_name)
            
            if df.empty:
                return False
            
            # Build condition mask
            mask = pd.Series([True] * len(df))
            for column, value in condition.items():
                if column in df.columns:
                    mask = mask & (df[column] == value)
                else:
                    raise CSVValidationError(f"Column '{column}' not found in CSV")
            
            # Count rows to update
            rows_to_update = mask.sum()
            
            if rows_to_update == 0:
                return False
            
            # Apply updates
            sanitized_updates = sanitize_csv_data(updates)
            for column, value in sanitized_updates.items():
                if column in df.columns:
                    df.loc[mask, column] = value
                else:
                    raise CSVValidationError(f"Column '{column}' not found in CSV")
            
            # Write back
            await self.write_csv(file_name, df)
            
            data_logger.log_data_operation(
                "update", file_name, True,
                error_details=f"Updated {rows_to_update} rows in blob"
            )
            
            return True
            
        except Exception as e:
            data_logger.log_data_operation(
                "update", file_name, False,
                error_details=str(e)
            )
            raise StorageError(f"Failed to update CSV blob: {str(e)}", file_name, "update")
    
    async def backup_file(self, file_name: str) -> bool:
        """Create backup of CSV blob."""
        try:
            if not await self.file_exists(file_name):
                return False
            
            # Create backup blob name with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backups/{file_name.replace('.csv', '')}_{timestamp}.csv"
            
            blob_name = self._get_blob_name(file_name)
            backup_blob_name = self._get_blob_name(backup_name)
            
            client = await self._get_client()
            source_blob = client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )
            backup_blob = client.get_blob_client(
                container=self.config.container_name,
                blob=backup_blob_name
            )
            
            # Copy blob
            source_url = source_blob.url
            await backup_blob.start_copy_from_url(source_url)
            
            data_logger.log_data_operation(
                "backup", file_name, True,
                error_details=f"Backup created: {backup_name}"
            )
            
            return True
            
        except Exception as e:
            data_logger.log_data_operation(
                "backup", file_name, False,
                error_details=str(e)
            )
            return False
    
    async def get_file_info(self, file_name: str) -> Dict[str, Any]:
        """Get blob metadata information."""
        blob_name = self._get_blob_name(file_name)
        
        try:
            client = await self._get_client()
            blob_client = client.get_blob_client(
                container=self.config.container_name,
                blob=blob_name
            )
            
            if not await blob_client.exists():
                return {"exists": False}
            
            properties = await blob_client.get_blob_properties()
            df = await self.read_csv(file_name)
            
            return {
                "exists": True,
                "size_bytes": properties.size,
                "modified": properties.last_modified.isoformat(),
                "etag": properties.etag,
                "rows": len(df) if not df.empty else 0,
                "columns": list(df.columns) if not df.empty else [],
                "blob_name": blob_name,
                "content_type": properties.content_settings.content_type
            }
            
        except Exception as e:
            raise StorageError(f"Failed to get blob info: {str(e)}", file_name, "info")
    
    async def _blob_lease(self, file_name: str):
        """Context manager for blob lease to handle concurrent access."""
        return AzureBlobLease(self, file_name, self.lock_timeout)


class AzureBlobLease:
    """
    Blob lease context manager for concurrent access control.
    """
    
    def __init__(self, storage: AzureStorage, file_name: str, timeout: int = 30):
        self.storage = storage
        self.file_name = file_name
        self.timeout = timeout
        self.blob_client = None
        self.lease_client = None
        self.lease_id = None
    
    async def __aenter__(self):
        """Acquire blob lease."""
        blob_name = self.storage._get_blob_name(self.file_name)
        client = await self.storage._get_client()
        
        self.blob_client = client.get_blob_client(
            container=self.storage.config.container_name,
            blob=blob_name
        )
        
        # Try to acquire lease
        start_time = datetime.utcnow()
        while (datetime.utcnow() - start_time).seconds < self.timeout:
            try:
                self.lease_client = self.blob_client.acquire_lease(lease_duration=60)
                self.lease_id = self.lease_client.id
                return self.blob_client
            except Exception:
                await asyncio.sleep(1)
        
        raise StorageError(f"Could not acquire lease for {self.file_name} within {self.timeout}s")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release blob lease."""
        if self.lease_client:
            try:
                await self.lease_client.release()
            except Exception:
                pass  # Lease will expire automatically
