"""
Plutus Backend - Balance Management Schemas (Simplified)
Pydantic models for balance check operation only.

Team: Yay!
Date: August 30, 2025
"""

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    """Simplified response model for balance check."""
    user_id: str
    account_number: str
    balance: float
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "USR12345678",
                "account_number": "1234567890123456",
                "balance": 8750.50
            }
        }
