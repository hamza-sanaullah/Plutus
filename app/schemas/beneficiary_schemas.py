"""
Plutus Backend - Beneficiary Management Schemas
Pydantic models for beneficiary operations (add, list, remove).

Team: Yay!
Date: August 29, 2025
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime

from .base_schemas import BaseResponse, CommonValidators, PaginatedResponse


class BeneficiaryAddRequest(BaseModel):
    """Request model for adding a new beneficiary."""
    name: str = Field(..., description="Beneficiary display name")
    bank_name: str = Field(..., description="Beneficiary's bank name")
    account_number: str = Field(..., description="Beneficiary's account number")
    iban: Optional[str] = Field(None, description="International Bank Account Number (optional)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate beneficiary name."""
        return CommonValidators.validate_beneficiary_name(v)

    @field_validator('bank_name')
    @classmethod
    def validate_bank_name(cls, v):
        """Validate bank name."""
        return CommonValidators.validate_bank_name(v)

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        """Validate account number format."""
        return CommonValidators.validate_account_number(v)
    
    @field_validator('iban')
    @classmethod
    def validate_iban(cls, v):
        """Validate IBAN format."""
        if v is not None:
            return CommonValidators.validate_iban(v)
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Zunaira",
                "bank_name": "Habib Bank Limited",
                "account_number": "9876543210987654"
            }
        }


class BeneficiaryAddResponse(BaseResponse):
    """Response model for adding beneficiary."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Beneficiary added successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "beneficiary_id": "BEN12345678",
                    "name": "Zunaira",
                    "bank_name": "Habib Bank Limited",
                    "account_number": "9876543210987654",
                    "added_at": "2025-08-29T10:30:00Z"
                }
            }
        }


class BeneficiaryListRequest(BaseModel):
    """Request model for listing beneficiaries."""
    search_name: Optional[str] = Field(None, description="Search by beneficiary name")
    bank_filter: Optional[str] = Field(None, description="Filter by bank name")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @field_validator('search_name')
    @classmethod
    def validate_search_name(cls, v):
        """Validate search name."""
        if v and len(v.strip()) < 2:
            raise ValueError("Search name must be at least 2 characters")
        return v.strip() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "search_name": "Zunaira",
                "bank_filter": "HBL",
                "page": 1,
                "page_size": 20
            }
        }


class BeneficiaryListResponse(PaginatedResponse):
    """Response model for listing beneficiaries."""
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Beneficiaries retrieved successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": [
                    {
                        "beneficiary_id": "BEN12345678",
                        "name": "Zunaira",
                        "bank_name": "Habib Bank Limited",
                        "account_number": "9876543210987654",
                        "added_at": "2025-08-29T10:20:00Z"
                    },
                    {
                        "beneficiary_id": "BEN87654321",
                        "name": "Husnain",
                        "bank_name": "United Bank Limited",
                        "account_number": "5555666677778888",
                        "added_at": "2025-08-29T10:25:00Z"
                    }
                ],
                "pagination": {
                    "current_page": 1,
                    "page_size": 20,
                    "total_items": 5,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
        }


class BeneficiaryRemoveResponse(BaseResponse):
    """Response model for removing beneficiary."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Beneficiary removed successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "beneficiary_id": "BEN12345678",
                    "name": "Zunaira",
                    "removed_at": "2025-08-29T10:30:00Z"
                }
            }
        }


class BeneficiaryUpdateRequest(BaseModel):
    """Request model for updating beneficiary details."""
    name: Optional[str] = Field(None, description="New beneficiary name")
    bank_name: Optional[str] = Field(None, description="New bank name")
    account_number: Optional[str] = Field(None, description="New account number")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate beneficiary name."""
        if v is not None:
            return CommonValidators.validate_beneficiary_name(v)
        return v
    
    @field_validator('bank_name')
    @classmethod
    def validate_bank_name(cls, v):
        """Validate bank name."""
        if v is not None:
            return CommonValidators.validate_bank_name(v)
        return v
    
    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        """Validate account number."""
        if v is not None:
            return CommonValidators.validate_account_number(v)
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_at_least_one_field(cls, values):
        """Ensure at least one field is provided for update."""
        if isinstance(values, dict):
            if not any([values.get('name'), values.get('bank_name'), values.get('account_number')]):
                raise ValueError("At least one field must be provided for update")
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Zunaira Khan",
                "bank_name": "HBL Bank",
                "account_number": "9876543210987654"
            }
        }


class BeneficiaryUpdateResponse(BaseResponse):
    """Response model for updating beneficiary."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Beneficiary updated successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "beneficiary_id": "BEN12345678",
                    "name": "Zunaira Khan",
                    "bank_name": "HBL Bank",
                    "account_number": "9876543210987654",
                    "updated_at": "2025-08-29T10:30:00Z"
                }
            }
        }


class BeneficiaryDetailsResponse(BaseResponse):
    """Response model for getting beneficiary details."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Beneficiary details retrieved",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "beneficiary_id": "BEN12345678",
                    "name": "Zunaira",
                    "bank_name": "Habib Bank Limited",
                    "account_number": "9876543210987654",
                    "added_at": "2025-08-29T10:20:00Z",
                    "last_transaction": "2025-08-29T09:45:00Z",
                    "total_transactions": 5,
                    "total_amount_sent": 12500.0
                }
            }
        }


class BeneficiarySearchRequest(BaseModel):
    """Request model for searching beneficiaries by name."""
    query: str = Field(..., min_length=1, description="Search query")
    exact_match: bool = Field(default=False, description="Whether to search for exact match")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate search query."""
        if len(v.strip()) < 1:
            raise ValueError("Search query cannot be empty")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Zunaira",
                "exact_match": False
            }
        }


class BeneficiarySearchResponse(BaseResponse):
    """Response model for beneficiary search."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Search completed",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "query": "Zunaira",
                    "matches": [
                        {
                            "beneficiary_id": "BEN12345678",
                            "name": "Zunaira",
                            "bank_name": "Habib Bank Limited",
                            "account_number": "9876543210987654"
                        }
                    ],
                    "total_matches": 1
                }
            }
        }


# Internal models for data processing
class BeneficiaryData(BaseModel):
    """Internal model for beneficiary data."""
    owner_user_id: str
    beneficiary_id: str
    name: str
    bank_name: str
    account_number: str
    added_at: datetime
    
    class Config:
        orm_mode = True


class BeneficiaryValidationResult(BaseModel):
    """Model for beneficiary validation result."""
    is_valid: bool
    beneficiary_id: Optional[str] = None
    beneficiary_data: Optional[BeneficiaryData] = None
    error_message: Optional[str] = None
