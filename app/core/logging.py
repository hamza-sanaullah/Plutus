"""
Plutus Backend - Logging Configuration
Structured logging setup for audit trails and debugging.

Team: Yay!
Date: August 29, 2025
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import json

from .config import get_settings


class PlutusLogger:
    """
    Custom logger for Plutus Backend with structured logging and audit capabilities.
    """
    
    def __init__(self, name: str = "plutus"):
        self.settings = get_settings()
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with appropriate handlers and formatters."""
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        log_level = getattr(logging, self.settings.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(self.settings.log_format)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for production
        if not self.settings.debug:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"plutus_{datetime.now().strftime('%Y-%m-%d')}.log"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message with optional extra data."""
        self._log_with_extra(logging.INFO, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message with optional extra data."""
        self._log_with_extra(logging.ERROR, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message with optional extra data."""
        self._log_with_extra(logging.WARNING, message, extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message with optional extra data."""
        self._log_with_extra(logging.DEBUG, message, extra)
    
    def _log_with_extra(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal method to log with extra context."""
        if extra:
            message = f"{message} | Extra: {json.dumps(extra, default=str)}"
        self.logger.log(level, message)
    
    def log_api_request(
        self,
        method: str,
        endpoint: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log API request for audit trail."""
        extra_data = {
            "event_type": "api_request",
            "method": method,
            "endpoint": endpoint,
            "user_id": user_id,
            "request_id": request_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.info(f"API Request: {method} {endpoint}", extra_data)
    
    def log_authentication(
        self,
        event: str,
        username: str,
        success: bool,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log authentication events."""
        extra_data = {
            "event_type": "authentication",
            "event": event,
            "username": username,
            "success": success,
            "request_id": request_id,
            "ip_address": ip_address,
            "error_details": error_details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.info(f"Auth Success: {event} for {username}", extra_data)
        else:
            self.warning(f"Auth Failed: {event} for {username}", extra_data)
    
    def log_transaction(
        self,
        transaction_id: str,
        from_user: str,
        to_user: str,
        amount: float,
        status: str,
        request_id: Optional[str] = None
    ):
        """Log financial transactions for audit."""
        extra_data = {
            "event_type": "transaction",
            "transaction_id": transaction_id,
            "from_user": from_user,
            "to_user": to_user,
            "amount": amount,
            "status": status,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.info(f"Transaction {status}: {transaction_id}", extra_data)
    
    def log_balance_operation(
        self,
        user_id: str,
        operation: str,
        amount: float,
        new_balance: float,
        request_id: Optional[str] = None
    ):
        """Log balance changes for audit."""
        extra_data = {
            "event_type": "balance_operation",
            "user_id": user_id,
            "operation": operation,
            "amount": amount,
            "new_balance": new_balance,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.info(f"Balance {operation}: {user_id}", extra_data)
    
    def log_beneficiary_operation(
        self,
        user_id: str,
        operation: str,
        beneficiary_name: str,
        beneficiary_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log beneficiary operations for audit."""
        extra_data = {
            "event_type": "beneficiary_operation",
            "user_id": user_id,
            "operation": operation,
            "beneficiary_name": beneficiary_name,
            "beneficiary_id": beneficiary_id,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.info(f"Beneficiary {operation}: {beneficiary_name}", extra_data)
    
    def log_security_event(
        self,
        event: str,
        user_id: Optional[str] = None,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """Log security-related events."""
        extra_data = {
            "event_type": "security_event",
            "event": event,
            "user_id": user_id,
            "severity": severity,
            "details": details,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if severity == "high":
            self.error(f"Security Alert: {event}", extra_data)
        elif severity == "medium":
            self.warning(f"Security Event: {event}", extra_data)
        else:
            self.info(f"Security Info: {event}", extra_data)
    
    def log_data_operation(
        self,
        operation: str,
        file_name: str,
        success: bool,
        user_id: Optional[str] = None,
        error_details: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log CSV/data file operations."""
        extra_data = {
            "event_type": "data_operation",
            "operation": operation,
            "file_name": file_name,
            "success": success,
            "user_id": user_id,
            "error_details": error_details,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.info(f"Data Operation: {operation} on {file_name}", extra_data)
        else:
            self.error(f"Data Operation Failed: {operation} on {file_name}", extra_data)


# Global logger instances
main_logger = PlutusLogger("plutus.main")
api_logger = PlutusLogger("plutus.api")
auth_logger = PlutusLogger("plutus.auth")
transaction_logger = PlutusLogger("plutus.transaction")
security_logger = PlutusLogger("plutus.security")
data_logger = PlutusLogger("plutus.data")


def get_logger(name: str = "plutus") -> PlutusLogger:
    """
    Get logger instance by name.
    """
    return PlutusLogger(name)


def setup_logging():
    """
    Setup logging configuration for the entire application.
    """
    # This function can be called during app startup
    # to ensure proper logging configuration
    main_logger.info("🔧 Logging system initialized")
    main_logger.info(f"📊 Log level: {get_settings().log_level}")
    main_logger.info(f"🔍 Debug mode: {get_settings().debug}")


# Convenience functions for common logging operations
def log_startup():
    """Log application startup."""
    main_logger.info("🚀 Plutus Banking Backend starting up...")


def log_shutdown():
    """Log application shutdown."""
    main_logger.info("🛑 Plutus Banking Backend shutting down...")


def log_request(method: str, endpoint: str, user_id: str = None, request_id: str = None):
    """Log API request."""
    api_logger.log_api_request(method, endpoint, user_id, request_id)


def log_auth_success(username: str, request_id: str = None):
    """Log successful authentication."""
    auth_logger.log_authentication("login", username, True, request_id)


def log_auth_failure(username: str, error: str, request_id: str = None):
    """Log failed authentication."""
    auth_logger.log_authentication("login", username, False, request_id, error_details=error)
