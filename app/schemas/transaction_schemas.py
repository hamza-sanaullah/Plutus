"""
Plutus Backend - Transaction Management Schemas
Pydantic models for transaction operations (send, list, statement).

Team: Yay!
Date: August 29, 2025
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime

from .base_schemas import (
    BaseResponse, 
    CommonValidators, 
    PaginatedResponse, 
    TransactionStatus,
    Currency,
    DateTimeFilter,
    AmountFilter
)


class TransactionSendRequest(BaseModel):
    """Request model for sending money."""
    to_beneficiary_name: str = Field(..., description="Beneficiary name (must exist in beneficiaries list)")
    amount: float = Field(..., gt=0, description="Amount to send")
    description: Optional[str] = Field(None, max_length=200, description="Transaction description")
    currency: Currency = Field(default=Currency.PKR, description="Currency code")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate amount."""
        return CommonValidators.validate_amount(v)
    @field_validator('to_beneficiary_name')
    @classmethod
    def validate_beneficiary_name(cls, v):
        """Validate to_beneficiary_name."""
        return CommonValidators.validate_beneficiary_name(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate transaction description."""
        if v and len(v.strip()) == 0:
            return None
        return v.strip() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "to_beneficiary_name": "Zunaira",
                "amount": 500.0,
                "description": "Payment for services",
                "currency": "PKR"
            }
        }


class TransactionSendResponse(BaseResponse):
    """Response model for sending money."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Transaction completed successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "transaction_id": "TXN20250829103001",
                    "from_user_id": "USR12345678",
                    "to_beneficiary": "Zunaira",
                    "to_account": "9876543210987654",
                    "amount": 500.0,
                    "currency": "PKR",
                    "description": "Payment for services",
                    "status": "success",
                    "timestamp": "2025-08-29T10:30:00Z",
                    "sender_new_balance": 9750.50,
                    "daily_total_sent": 3000.0,
                    "remaining_daily_limit": 12000.0
                }
            }
        }


class TransactionListRequest(BaseModel):
    """Request model for listing transactions."""
    status_filter: Optional[TransactionStatus] = Field(None, description="Filter by transaction status")
    date_filter: Optional[DateTimeFilter] = Field(None, description="Date range filter")
    amount_filter: Optional[AmountFilter] = Field(None, description="Amount range filter")
    beneficiary_name: Optional[str] = Field(None, description="Filter by beneficiary name")
    transaction_type: Optional[str] = Field(None, description="Filter by type (sent/received)")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        """Validate transaction type."""
        if v and v.lower() not in ['sent', 'received', 'all']:
            raise ValueError("Transaction type must be 'sent', 'received', or 'all'")
        return v.lower() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "status_filter": "success",
                "date_filter": {
                    "start_date": "2025-08-01T00:00:00Z",
                    "end_date": "2025-08-29T23:59:59Z"
                },
                "amount_filter": {
                    "min_amount": 100.0,
                    "max_amount": 5000.0
                },
                "beneficiary_name": "Zunaira",
                "transaction_type": "sent",
                "page": 1,
                "page_size": 20
            }
        }


class TransactionListResponse(PaginatedResponse):
    """Response model for listing transactions."""
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Transactions retrieved successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": [
                    {
                        "transaction_id": "TXN20250829103001",
                        "type": "sent",
                        "to_beneficiary": "Zunaira",
                        "to_account": "9876543210987654",
                        "amount": 500.0,
                        "currency": "PKR",
                        "status": "success",
                        "description": "Payment for services",
                        "timestamp": "2025-08-29T10:30:00Z"
                    },
                    {
                        "transaction_id": "TXN20250829102002",
                        "type": "received",
                        "from_user": "Ahmed",
                        "from_account": "7777888899990000",
                        "amount": 300.0,
                        "currency": "PKR",
                        "status": "success",
                        "description": "Refund",
                        "timestamp": "2025-08-29T10:15:00Z"
                    }
                ],
                "pagination": {
                    "current_page": 1,
                    "page_size": 20,
                    "total_items": 45,
                    "total_pages": 3,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }


class TransactionDetailsResponse(BaseResponse):
    """Response model for transaction details."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Transaction details retrieved",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "transaction_id": "TXN20250829103001",
                    "from_user_id": "USR12345678",
                    "from_account": "1234567890123456",
                    "to_beneficiary": "Zunaira",
                    "to_account": "9876543210987654",
                    "amount": 500.0,
                    "currency": "PKR",
                    "status": "success",
                    "description": "Payment for services",
                    "timestamp": "2025-08-29T10:30:00Z",
                    "processing_time": "1.2s",
                    "fee_charged": 0.0,
                    "exchange_rate": 1.0
                }
            }
        }


class TransactionStatementRequest(BaseModel):
    """Request model for generating transaction statement."""
    start_date: datetime = Field(..., description="Statement start date")
    end_date: datetime = Field(..., description="Statement end date")
    format: str = Field(default="pdf", description="Statement format (pdf/csv)")
    include_balance_history: bool = Field(default=True, description="Include balance changes")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if v and values.get('start_date'):
            if v <= values['start_date']:
                raise ValueError("End date must be after start date")
            
            # Check if date range is reasonable (max 1 year)
            days_diff = (v - values['start_date']).days
            if days_diff > 365:
                raise ValueError("Date range cannot exceed 1 year")
        return v
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        """Validate statement format."""
        if v.lower() not in ['pdf', 'csv']:
            raise ValueError("Format must be 'pdf' or 'csv'")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2025-08-01T00:00:00Z",
                "end_date": "2025-08-29T23:59:59Z",
                "format": "pdf",
                "include_balance_history": True
            }
        }


class TransactionStatementResponse(BaseResponse):
    """Response model for transaction statement generation."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Statement generated successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "statement_id": "STMT20250829103001",
                    "file_url": "https://storage.example.com/statements/STMT20250829103001.pdf",
                    "file_name": "statement_2025-08-01_to_2025-08-29.pdf",
                    "format": "pdf",
                    "generated_at": "2025-08-29T10:30:00Z",
                    "expires_at": "2025-09-29T10:30:00Z",
                    "summary": {
                        "period": "2025-08-01 to 2025-08-29",
                        "total_transactions": 45,
                        "total_sent": 15000.0,
                        "total_received": 8500.0,
                        "opening_balance": 5000.0,
                        "closing_balance": 8750.50
                    }
                }
            }
        }


class DailySummaryResponse(BaseResponse):
    """Response model for daily transaction summary."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Daily summary retrieved",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "date": "2025-08-29",
                    "total_sent": 2500.0,
                    "total_received": 300.0,
                    "transaction_count": 8,
                    "daily_limit": 15000.0,
                    "remaining_limit": 12500.0,
                    "limit_utilization": 16.67,
                    "largest_transaction": 500.0,
                    "average_transaction": 350.0
                }
            }
        }


class TransactionCancelRequest(BaseModel):
    """Request model for canceling a transaction."""
    reason: str = Field(..., description="Reason for cancellation")
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        """Validate cancellation reason."""
        if len(v.strip()) < 10:
            raise ValueError("Cancellation reason must be at least 10 characters")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "reason": "Transaction was sent to wrong beneficiary by mistake"
            }
        }


class TransactionCancelResponse(BaseResponse):
    """Response model for transaction cancellation."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Transaction canceled successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "transaction_id": "TXN20250829103001",
                    "original_status": "pending",
                    "new_status": "canceled",
                    "refund_amount": 500.0,
                    "canceled_at": "2025-08-29T10:30:00Z",
                    "reason": "Transaction was sent to wrong beneficiary by mistake"
                }
            }
        }


# Internal models for data processing
class TransactionData(BaseModel):
    """Internal model for transaction data."""
    transaction_id: str
    from_user_id: str
    to_user_id: Optional[str]
    from_account: str
    to_account: str
    amount: float
    status: TransactionStatus
    description: Optional[str]
    timestamp: datetime
    daily_total_sent: float
    
    class Config:
        orm_mode = True
        use_enum_values = True


class TransactionValidationResult(BaseModel):
    """Model for transaction validation result."""
    is_valid: bool
    error_message: Optional[str] = None
    beneficiary_found: bool = False
    sufficient_balance: bool = False
    within_daily_limit: bool = False
    validation_details: Optional[dict] = None


class TransactionStatusRequest(BaseModel):
    """Request model for checking transaction status."""
    transaction_id: str = Field(..., description="Transaction ID to check")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN123456789"
            }
        }


class TransactionRequest(BaseModel):
    """Request model for sending money (compatible with service layer)."""
    beneficiary_id: str = Field(..., description="Beneficiary ID to send money to")
    amount: float = Field(..., gt=0, description="Amount to send")
    description: Optional[str] = Field(None, max_length=200, description="Transaction description")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate amount is positive and reasonable."""
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        if v > 500000:  # Maximum PKR 500,000 per transaction
            raise ValueError("Amount cannot exceed PKR 500,000 per transaction")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "beneficiary_id": "BEN123456789",
                "amount": 5000.0,
                "description": "Monthly allowance transfer"
            }
        }


# Aliases for backward compatibility
TransactionHistoryRequest = TransactionListRequest
