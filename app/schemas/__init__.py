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

# Authentication schemas
from .auth_schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserRegistrationResponse,
    UserLoginResponse,
    TokenValidationResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    UserProfileResponse,
    LogoutResponse,
    UserData,
    TokenData
)

# Balance schemas
from .balance_schemas import (
    BalanceCheckResponse,
    DepositRequest,
    DepositResponse,
    WithdrawRequest,
    WithdrawResponse,
    BalanceHistoryRequest,
    BalanceHistoryResponse,
    DailyLimitUpdateRequest,
    DailyLimitUpdateResponse,
    BalanceOperation
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
    TransactionSendRequest,
    TransactionSendResponse,
    TransactionListRequest,
    TransactionListResponse,
    TransactionDetailsResponse,
    TransactionStatementRequest,
    TransactionStatementResponse,
    DailySummaryResponse,
    TransactionCancelRequest,
    TransactionCancelResponse,
    TransactionData,
    TransactionValidationResult
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
    
    # Authentication schemas
    "UserRegistrationRequest",
    "UserLoginRequest",
    "UserRegistrationResponse",
    "UserLoginResponse",
    "TokenValidationResponse",
    "PasswordChangeRequest",
    "PasswordChangeResponse",
    "UserProfileResponse",
    "LogoutResponse",
    "UserData",
    "TokenData",
    
    # Balance schemas
    "BalanceCheckResponse",
    "DepositRequest",
    "DepositResponse",
    "WithdrawRequest",
    "WithdrawResponse",
    "BalanceHistoryRequest",
    "BalanceHistoryResponse",
    "DailyLimitUpdateRequest",
    "DailyLimitUpdateResponse",
    "BalanceOperation",
    
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
    "TransactionSendRequest",
    "TransactionSendResponse",
    "TransactionListRequest",
    "TransactionListResponse",
    "TransactionDetailsResponse",
    "TransactionStatementRequest",
    "TransactionStatementResponse",
    "DailySummaryResponse",
    "TransactionCancelRequest",
    "TransactionCancelResponse",
    "TransactionData",
    "TransactionValidationResult"
]
