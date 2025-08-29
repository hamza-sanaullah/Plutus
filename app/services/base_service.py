"""
Plutus Backend - Base Service Class
Abstract base class for all business services with common functionality.

Team: Yay!
Date: August 29, 2025
"""

from abc import ABC
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from ..storage import StorageManager, get_storage_manager
from ..core.config import get_settings
from ..core.logging import PlutusLogger, get_logger
from ..core.security import SecurityUtils, get_security_utils, create_audit_log_entry


class BaseService(ABC):
    """
    Base service class providing common functionality for all business services.
    """
    
    def __init__(self):
        self.storage: StorageManager = get_storage_manager()
        self.settings = get_settings()
        self.security: SecurityUtils = get_security_utils()
        self.logger: PlutusLogger = get_logger(self.__class__.__name__)
        
    async def log_audit(
        self,
        user_id: str,
        action: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> bool:
        """
        Log audit entry for compliance and tracking.
        """
        try:
            audit_entry = create_audit_log_entry(
                user_id=user_id,
                action=action,
                details=details,
                ip_address=ip_address,
                request_id=request_id
            )
            
            success = await self.storage.append_csv(
                self.settings.audit_logs_csv,
                audit_entry
            )
            
            if success:
                self.logger.info(f"Audit logged: {action} for user {user_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to log audit: {str(e)}")
            return False
    
    def generate_id(self, prefix: str) -> str:
        """
        Generate unique ID with given prefix.
        """
        return f"{prefix}{uuid.uuid4().hex[:8].upper()}"
    
    def create_timestamp(self) -> str:
        """
        Create ISO timestamp for records.
        """
        return datetime.utcnow().isoformat() + "Z"
    
    def format_currency(self, amount: float, currency: str = "PKR") -> str:
        """
        Format amount with currency.
        """
        return f"{currency} {amount:,.2f}"
    
    def validate_business_hours(self) -> bool:
        """
        Check if current time is within business hours.
        Can be extended for specific banking hour restrictions.
        """
        # For now, allow 24/7 operations
        # Can be modified to restrict to business hours if needed
        return True
    
    def calculate_fee(self, amount: float, transaction_type: str) -> float:
        """
        Calculate transaction fee based on amount and type.
        """
        # Basic fee structure - can be enhanced
        if transaction_type == "transfer":
            if amount <= 1000:
                return 0.0  # Free for small amounts
            elif amount <= 10000:
                return 5.0  # Fixed fee for medium amounts
            else:
                return amount * 0.001  # 0.1% for large amounts
        
        return 0.0  # No fee for other operations
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by user ID.
        """
        try:
            users_df = await self.storage.read_csv(self.settings.users_csv)
            
            if users_df.empty:
                return None
            
            user_rows = users_df[users_df['user_id'] == user_id]
            
            if user_rows.empty:
                return None
            
            return user_rows.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to get user {user_id}: {str(e)}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by username.
        """
        try:
            users_df = await self.storage.read_csv(self.settings.users_csv)
            
            if users_df.empty:
                return None
            
            user_rows = users_df[users_df['username'] == username.lower()]
            
            if user_rows.empty:
                return None
            
            return user_rows.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to get user by username {username}: {str(e)}")
            return None
    
    async def get_user_by_account_number(self, account_number: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by account number.
        """
        try:
            users_df = await self.storage.read_csv(self.settings.users_csv)
            
            if users_df.empty:
                return None
            
            user_rows = users_df[users_df['account_number'] == account_number]
            
            if user_rows.empty:
                return None
            
            return user_rows.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to get user by account {account_number}: {str(e)}")
            return None
    
    async def update_user_balance(
        self,
        user_id: str,
        new_balance: float,
        operation: str,
        amount: float,
        description: str = None
    ) -> bool:
        """
        Update user balance and log the operation.
        """
        try:
            # Update balance in users CSV
            success = await self.storage.update_row(
                self.settings.users_csv,
                {"user_id": user_id},
                {"balance": new_balance}
            )
            
            if success:
                # Log balance operation
                await self.log_audit(
                    user_id=user_id,
                    action=f"balance_{operation}",
                    details={
                        "operation": operation,
                        "amount": amount,
                        "new_balance": new_balance,
                        "description": description
                    }
                )
                
                self.logger.info(
                    f"Balance updated for user {user_id}: {operation} {amount}, new balance: {new_balance}"
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update balance for user {user_id}: {str(e)}")
            return False
    
    async def check_daily_limit(self, user_id: str, amount: float) -> Dict[str, Any]:
        """
        Check if transaction amount is within daily limit.
        """
        try:
            # Get user's daily limit
            user = await self.get_user_by_id(user_id)
            if not user:
                return {"valid": False, "error": "User not found"}
            
            daily_limit = float(user.get('daily_limit', 0))
            
            # Calculate today's total sent
            today = datetime.utcnow().strftime("%Y-%m-%d")
            transactions_df = await self.storage.read_csv(self.settings.transactions_csv)
            
            if not transactions_df.empty:
                # Filter transactions for today and this user
                today_transactions = transactions_df[
                    (transactions_df['from_user_id'] == user_id) &
                    (transactions_df['timestamp'].str.startswith(today)) &
                    (transactions_df['status'] == 'success')
                ]
                
                daily_total = today_transactions['amount'].sum() if not today_transactions.empty else 0.0
            else:
                daily_total = 0.0
            
            # Check if new transaction would exceed limit
            new_total = daily_total + amount
            
            return {
                "valid": new_total <= daily_limit,
                "daily_limit": daily_limit,
                "daily_spent": daily_total,
                "new_total": new_total,
                "remaining_limit": max(0, daily_limit - new_total)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check daily limit for user {user_id}: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def create_error_response(self, message: str, error_code: str = None) -> Dict[str, Any]:
        """
        Create standardized error response.
        """
        return {
            "status": "failed",
            "message": message,
            "error_code": error_code,
            "timestamp": self.create_timestamp()
        }
    
    def create_success_response(self, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create standardized success response.
        """
        response = {
            "status": "success",
            "message": message,
            "timestamp": self.create_timestamp()
        }
        
        if data:
            response["data"] = data
        
        return response
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for this service.
        """
        try:
            # Check storage connectivity
            storage_health = await self.storage.get_storage_health()
            
            return {
                "service": self.__class__.__name__,
                "status": "healthy" if storage_health["status"] == "healthy" else "degraded",
                "storage": storage_health,
                "timestamp": self.create_timestamp()
            }
            
        except Exception as e:
            return {
                "service": self.__class__.__name__,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": self.create_timestamp()
            }
