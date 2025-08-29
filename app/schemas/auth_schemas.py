"""
Plutus Backend - Authentication Schemas
Pydantic models for user authentication and registration.

Team: Yay!
Date: August 29, 2025
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from .base_schemas import BaseResponse, CommonValidators


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., description="Unique username for the account")
    password: str = Field(..., description="User password (minimum 8 characters)")
    account_number: str = Field(..., description="User's bank account number")
    initial_balance: Optional[float] = Field(default=1000.0, ge=0, description="Starting balance")
    daily_limit: Optional[float] = Field(default=10000.0, ge=1000, description="Daily transaction limit")
    
    # Validators
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username."""
        return CommonValidators.validate_username(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password."""
        return CommonValidators.validate_password(v)
    
    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        """Validate account_number."""
        return CommonValidators.validate_account_number(v)
    
    @field_validator('daily_limit')
    @classmethod
    def validate_daily_limit(cls, v):
        """Validate daily limit is reasonable."""
        if v and v > 100000:  # Maximum daily limit of PKR 100,000
            raise ValueError("Daily limit cannot exceed PKR 100,000")
        return v
        if v < initial_balance:
            raise ValueError("Daily limit should be at least equal to initial balance")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "MySecure123!",
                "account_number": "1234567890123456",
                "initial_balance": 5000.0,
                "daily_limit": 15000.0
            }
        }


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "MySecure123!"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserRegistrationResponse(BaseResponse):
    """Response model for user registration."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "User registered successfully",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "user_id": "USR12345678",
                    "username": "john_doe",
                    "account_number": "1234567890123456",
                    "balance": 5000.0,
                    "daily_limit": 15000.0,
                    "created_at": "2025-08-29T10:30:00Z"
                }
            }
        }


class UserLoginResponse(BaseResponse):
    """Response model for user login."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Login successful",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "user_info": {
                        "user_id": "USR12345678",
                        "username": "john_doe",
                        "account_number": "1234567890123456"
                    }
                }
            }
        }


class TokenValidationResponse(BaseResponse):
    """Response model for token validation."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Token is valid",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "user_id": "USR12345678",
                    "username": "john_doe",
                    "account_number": "1234567890123456",
                    "token_expires_at": "2025-08-29T11:00:00Z"
                }
            }
        }


class PasswordChangeRequest(BaseModel):
    """Request model for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new_password."""
        return CommonValidators.validate_password(v)
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecure456#"
            }
        }


class PasswordChangeResponse(BaseResponse):
    """Response model for password change."""
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Password changed successfully",
                "timestamp": "2025-08-29T10:30:00Z"
            }
        }


class UserProfileResponse(BaseResponse):
    """Response model for user profile information."""
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "User profile retrieved",
                "timestamp": "2025-08-29T10:30:00Z",
                "data": {
                    "user_id": "USR12345678",
                    "username": "john_doe",
                    "account_number": "1234567890123456",
                    "balance": 8750.50,
                    "daily_limit": 15000.0,
                    "created_at": "2025-08-29T09:00:00Z",
                    "last_login": "2025-08-29T10:00:00Z"
                }
            }
        }


class LogoutResponse(BaseResponse):
    """Response model for user logout."""
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Logged out successfully",
                "timestamp": "2025-08-29T10:30:00Z"
            }
        }


# Internal models for data processing
class UserData(BaseModel):
    """Internal model for user data."""
    user_id: str
    username: str
    hashed_password: str
    account_number: str
    balance: float
    daily_limit: float
    created_at: datetime
    
    class Config:
        orm_mode = True


class TokenData(BaseModel):
    """Internal model for JWT token data."""
    sub: str  # user_id
    username: str
    account_number: str
    exp: datetime
    iat: datetime
    jti: str  # JWT ID
