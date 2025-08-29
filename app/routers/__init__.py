"""
Plutus Backend - Routers Package
API route handlers for the banking application.

Team: Yay!
Date: August 29, 2025
"""

from .auth_router import router as auth_router
from .balance_router import router as balance_router
from .beneficiary_router import router as beneficiary_router
from .transaction_router import router as transaction_router

__all__ = [
    "auth_router",
    "balance_router", 
    "beneficiary_router",
    "transaction_router"
]
