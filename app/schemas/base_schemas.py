"""
Plutus Backend - Base Pydantic Schemas
Common base models and validators for API data validation.

Team: Yay!
Date: August 29, 2025
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response status values."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    ERROR = "error"


class TransactionStatus(str, Enum):
    """Transaction status values."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Currency(str, Enum):
    """Supported currencies."""
    PKR = "PKR"
    USD = "USD"


class BaseResponse(BaseModel):
    """Base response model for all API endpoints."""
    status: ResponseStatus
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class ErrorResponse(BaseResponse):
    """Error response model."""
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseResponse):
    """Success response model."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseResponse):
    """Paginated response model."""
    data: List[Any] = []
    pagination: Dict[str, Any] = {}
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total_count: int,
        pagination: PaginationParams,
        status: ResponseStatus = ResponseStatus.SUCCESS
    ):
        """Create paginated response."""
        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size
        
        return cls(
            status=status,
            data=items,
            pagination={
                "current_page": pagination.page,
                "page_size": pagination.page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": pagination.page < total_pages,
                "has_previous": pagination.page > 1
            }
        )


# Common validators
class CommonValidators:
    """Common validation functions."""
    
    @staticmethod
    def validate_account_number(value: str) -> str:
        """Validate account number format."""
        if not value:
            raise ValueError("Account number is required")
        
        # Remove spaces and hyphens
        clean_number = value.replace("-", "").replace(" ", "")
        
        if not clean_number.isdigit():
            raise ValueError("Account number must contain only digits")
        
        if len(clean_number) < 10 or len(clean_number) > 20:
            raise ValueError("Account number must be between 10-20 digits")
        
        if len(set(clean_number)) == 1:
            raise ValueError("Account number cannot be all same digits")
        
        return clean_number
    
    @staticmethod
    def validate_amount(value: float) -> float:
        """Validate monetary amount."""
        if value <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if value > 50000:  # Max transaction limit
            raise ValueError("Amount exceeds maximum transaction limit")
        
        # Round to 2 decimal places
        return round(value, 2)
    
    @staticmethod
    def validate_username(value: str) -> str:
        """Validate username format."""
        if not value:
            raise ValueError("Username is required")
        
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        if len(value) > 50:
            raise ValueError("Username must be less than 50 characters")
        
        if not value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        return value.lower()
    
    @staticmethod
    def validate_password(value: str) -> str:
        """Validate password strength."""
        if not value:
            raise ValueError("Password is required")
        
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in value):
            raise ValueError("Password must contain at least one special character")
        
        return value
    
    @staticmethod
    def validate_bank_name(value: str) -> str:
        """Validate bank name."""
        if not value:
            raise ValueError("Bank name is required")
        
        if len(value.strip()) < 3:
            raise ValueError("Bank name must be at least 3 characters")
        
        return value.strip()
    
    @staticmethod
    def validate_beneficiary_name(value: str) -> str:
        """Validate beneficiary name."""
        if not value:
            raise ValueError("Beneficiary name is required")
        
        if len(value.strip()) < 2:
            raise ValueError("Beneficiary name must be at least 2 characters")
        
        if len(value.strip()) > 100:
            raise ValueError("Beneficiary name must be less than 100 characters")
        
        return value.strip()


class DateTimeFilter(BaseModel):
    """Date time filter for queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if v and values.get('start_date'):
            if v <= values['start_date']:
                raise ValueError("End date must be after start date")
        return v


class AmountFilter(BaseModel):
    """Amount filter for queries."""
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    
    @field_validator('max_amount')
    @classmethod
    def validate_amount_range(cls, v, values):
        """Validate that max_amount is greater than min_amount."""
        if v and values.get('min_amount'):
            if v <= values['min_amount']:
                raise ValueError("Max amount must be greater than min amount")
        return v
