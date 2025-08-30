"""
Plutus Backend - Transaction Management Schemas (Simplified)
Pydantic models for transaction operations - send money and history.

Team: Yay!
Date: August 30, 2025
"""

from pydantic import BaseModel, Field
from typing import List


class SendMoneyRequest(BaseModel):
    """Request model for sending money."""
    to_user_id: str = Field(..., description="Recipient user ID")
    amount: float = Field(..., gt=0, description="Amount to send")
    description: str = Field(..., description="Transaction description")
    
    class Config:
        schema_extra = {
            "example": {
                "to_user_id": "USR87654321",
                "amount": 500.0,
                "description": "Payment for services"
            }
        }


class SendMoneyResponse(BaseModel):
    """Response model for sending money."""
    transaction_id: str
    from_user_id: str
    to_user_id: str
    amount: float
    description: str
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "TXN20250830120001",
                "from_user_id": "USR12345678",
                "to_user_id": "USR87654321",
                "amount": 500.0,
                "description": "Payment for services",
                "timestamp": "2025-08-30T12:00:00Z"
            }
        }


class TransactionHistoryItem(BaseModel):
    """Model for individual transaction in history."""
    transaction_id: str
    from_user_id: str
    to_user_id: str
    amount: float
    description: str
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "TXN20250830120001",
                "from_user_id": "USR12345678",
                "to_user_id": "USR87654321",
                "amount": 500.0,
                "description": "Payment for services",
                "timestamp": "2025-08-30T12:00:00Z"
            }
        }


class TransactionHistoryResponse(BaseModel):
    """Response model for transaction history."""
    transactions: List[TransactionHistoryItem]
    
    class Config:
        schema_extra = {
            "example": {
                "transactions": [
                    {
                        "transaction_id": "TXN20250830120001",
                        "from_user_id": "USR12345678",
                        "to_user_id": "USR87654321",
                        "amount": 500.0,
                        "description": "Payment for services",
                        "timestamp": "2025-08-30T12:00:00Z"
                    },
                    {
                        "transaction_id": "TXN20250830110001",
                        "from_user_id": "USR87654321",
                        "to_user_id": "USR12345678",
                        "amount": 1000.0,
                        "description": "Refund",
                        "timestamp": "2025-08-30T11:00:00Z"
                    }
                ]
            }
        }
