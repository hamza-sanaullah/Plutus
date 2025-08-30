"""
Plutus Backend - Balance Management Service (Simplified)
Handles only balance checking operations.

Team: Yay!
Date: August 30, 2025
"""

from typing import Dict, Any
import pandas as pd
from decimal import Decimal

from .base_service import BaseService


class BalanceService(BaseService):
    """
    Simplified balance service for balance checking only.
    """
    
    async def check_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Check user balance with simplified response (user_id, account_number, balance only).
        """
        try:
            # Read users data
            users_df = await self.storage.read_csv(self.settings.users_csv)
            
            # Find user
            user_data = users_df[users_df['user_id'] == user_id]
            
            if user_data.empty:
                return {"error": "User not found"}
            
            user = user_data.iloc[0]
            
            # Simplified response with only essential data (no wrapper)
            return {
                "user_id": user_id,
                "account_number": str(user['account_number']),
                "balance": float(user['balance'])
            }
            
        except Exception as e:
            self.logger.error(f"Balance check failed for user {user_id}: {str(e)}")
            return {"error": "Failed to retrieve balance"}


def get_balance_service() -> BalanceService:
    """
    Get balance service instance.
    """
    return BalanceService()
