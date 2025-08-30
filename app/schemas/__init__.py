"""
Plutus Backend - Schemas Package
Pydantic models for API data validation and documentation.

Team: Yay!
Date: August 29, 2025
"""

# Base schemas
from .base_schemas import (
    ResponseStatus,
    TransactionStatus,
    Currency,
    BaseResponse,
    ErrorResponse,
    SuccessResponse,
    PaginationParams,
    PaginatedResponse,
    CommonValidators,
    DateTimeFilter,
    AmountFilter
)

# Balance schemas
from .balance_schemas import (
    BalanceResponse
)

# Beneficiary schemas
from .beneficiary_schemas import (
    BeneficiaryAddRequest,
    BeneficiaryAddResponse,
    BeneficiaryListRequest,
    BeneficiaryListResponse,
    BeneficiaryRemoveResponse,
    BeneficiaryUpdateRequest,
    BeneficiaryUpdateResponse,
    BeneficiaryDetailsResponse,
    BeneficiarySearchRequest,
    BeneficiarySearchResponse,
    BeneficiaryData,
    BeneficiaryValidationResult
)

# Transaction schemas
from .transaction_schemas import (
    SendMoneyRequest,
    SendMoneyResponse,
    TransactionHistoryItem,
    TransactionHistoryResponse
)

__all__ = [
    # Base schemas
    "ResponseStatus",
    "TransactionStatus",
    "Currency",
    "BaseResponse",
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "PaginatedResponse",
    "CommonValidators",
    "DateTimeFilter",
    "AmountFilter",
    
    # Balance schemas
    "BalanceResponse",
    
    # Beneficiary schemas
    "BeneficiaryAddRequest",
    "BeneficiaryAddResponse",
    "BeneficiaryListRequest",
    "BeneficiaryListResponse",
    "BeneficiaryRemoveResponse",
    "BeneficiaryUpdateRequest",
    "BeneficiaryUpdateResponse",
    "BeneficiaryDetailsResponse",
    "BeneficiarySearchRequest",
    "BeneficiarySearchResponse",
    "BeneficiaryData",
    "BeneficiaryValidationResult",
    
    # Transaction schemas
    "SendMoneyRequest",
    "SendMoneyResponse",
    "TransactionHistoryItem",
    "TransactionHistoryResponse"
]
