"""
Plutus Backend - Routers Package (Simplified)
API route handlers for the simplified banking application.

Team: Yay!
Date: August 30, 2025
"""

from .balance_router import router as balance_router
from .beneficiary_router import router as beneficiary_router
from .transaction_router import router as transaction_router

__all__ = [
    "balance_router", 
    "beneficiary_router",
    "transaction_router"
]
