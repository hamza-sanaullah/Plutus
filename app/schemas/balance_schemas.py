"""
Plutus Backend - Balance Management Schemas
Pydantic models for balance operations (check, deposit, withdraw).

Team: Yay!
Date: August 29, 2025
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime

from .base_schemas import BaseResponse, CommonValidators, Currency


class BalanceCheckResponse(BaseResponse):
    """Response model for balance check."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Balance retrieved successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "user_id": "USR12345678",
                    "account_number": "1234567890123456",
                    "current_balance": 8750.50,
                    "daily_limit": 15000.0,
                    "daily_spent_today": 2500.0,
                    "available_daily_limit": 12500.0,
                    "currency": "PKR",
                    "last_transaction": "2025-08-29T09:45:00Z"
                }
            }
        }


class DepositRequest(BaseModel):
    """Request model for balance deposit."""
    amount: float = Field(..., gt=0, description="Amount to deposit")
    description: Optional[str] = Field(None, max_length=200, description="Deposit description")
    currency: Currency = Field(default=Currency.PKR, description="Currency code")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate amount."""
        return CommonValidators.validate_amount(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate deposit description."""
        if v and len(v.strip()) == 0:
            return None
        return v.strip() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 2500.0,
                "description": "Salary deposit",
                "currency": "PKR"
            }
        }


class DepositResponse(BaseResponse):
    """Response model for balance deposit."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Deposit completed successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "transaction_id": "TXN20250829103001",
                    "user_id": "USR12345678",
                    "amount_deposited": 2500.0,
                    "previous_balance": 8750.50,
                    "new_balance": 11250.50,
                    "currency": "PKR",
                    "description": "Salary deposit",
                    "timestamp": "2025-08-29T10:30:00Z"
                }
            }
        }


class WithdrawRequest(BaseModel):
    """Request model for balance withdrawal."""
    amount: float = Field(..., gt=0, description="Amount to withdraw")
    description: Optional[str] = Field(None, max_length=200, description="Withdrawal description")
    currency: Currency = Field(default=Currency.PKR, description="Currency code")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate amount."""
        return CommonValidators.validate_amount(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate withdrawal description."""
        if v and len(v.strip()) == 0:
            return None
        return v.strip() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 1000.0,
                "description": "ATM withdrawal",
                "currency": "PKR"
            }
        }


class WithdrawResponse(BaseResponse):
    """Response model for balance withdrawal."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Withdrawal completed successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "transaction_id": "TXN20250829103002",
                    "user_id": "USR12345678",
                    "amount_withdrawn": 1000.0,
                    "previous_balance": 11250.50,
                    "new_balance": 10250.50,
                    "currency": "PKR",
                    "description": "ATM withdrawal",
                    "timestamp": "2025-08-29T10:30:00Z"
                }
            }
        }


class BalanceHistoryRequest(BaseModel):
    """Request model for balance history."""
    start_date: Optional[datetime] = Field(None, description="Start date for history")
    end_date: Optional[datetime] = Field(None, description="End date for history")
    transaction_type: Optional[str] = Field(None, description="Filter by transaction type (deposit/withdraw)")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if v and values.get('start_date'):
            if v <= values['start_date']:
                raise ValueError("End date must be after start date")
        return v
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        """Validate transaction type."""
        if v and v.lower() not in ['deposit', 'withdraw', 'all']:
            raise ValueError("Transaction type must be 'deposit', 'withdraw', or 'all'")
        return v.lower() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2025-08-01T00:00:00Z",
                "end_date": "2025-08-29T23:59:59Z",
                "transaction_type": "all",
                "page": 1,
                "page_size": 20
            }
        }


class BalanceHistoryResponse(BaseResponse):
    """Response model for balance history."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Balance history retrieved",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "transactions": [
                        {
                            "transaction_id": "TXN20250829103001",
                            "type": "deposit",
                            "amount": 2500.0,
                            "balance_before": 8750.50,
                            "balance_after": 11250.50,
                            "description": "Salary deposit",
                            "timestamp": "2025-08-29T10:30:00Z"
                        },
                        {
                            "transaction_id": "TXN20250829103002",
                            "type": "withdraw",
                            "amount": 1000.0,
                            "balance_before": 11250.50,
                            "balance_after": 10250.50,
                            "description": "ATM withdrawal",
                            "timestamp": "2025-08-29T10:35:00Z"
                        }
                    ],
                    "pagination": {
                        "current_page": 1,
                        "page_size": 20,
                        "total_items": 25,
                        "total_pages": 2,
                        "has_next": True,
                        "has_previous": False
                    },
                    "summary": {
                        "total_deposits": 15000.0,
                        "total_withdrawals": 4750.0,
                        "net_change": 10250.0,
                        "transaction_count": 25
                    }
                }
            }
        }


class DailyLimitUpdateRequest(BaseModel):
    """Request model for updating daily transaction limit."""
    new_daily_limit: float = Field(..., ge=1000, description="New daily transaction limit")
    
    @field_validator('new_daily_limit')
    @classmethod
    def validate_daily_limit(cls, v):
        """Validate daily limit."""
        if v > 100000:  # Maximum allowed daily limit
            raise ValueError("Daily limit cannot exceed 100,000")
        return round(v, 2)
    
    class Config:
        schema_extra = {
            "example": {
                "new_daily_limit": 25000.0
            }
        }


class DailyLimitUpdateResponse(BaseResponse):
    """Response model for daily limit update."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Daily limit updated successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "user_id": "USR12345678",
                    "previous_daily_limit": 15000.0,
                    "new_daily_limit": 25000.0,
                    "effective_date": "2025-08-29T10:30:00Z"
                }
            }
        }


# Internal models for data processing
class BalanceOperation(BaseModel):
    """Internal model for balance operations."""
    user_id: str
    operation_type: str  # deposit, withdraw
    amount: float
    previous_balance: float
    new_balance: float
    description: Optional[str]
    timestamp: datetime
    transaction_id: str
    
    class Config:
        orm_mode = True
