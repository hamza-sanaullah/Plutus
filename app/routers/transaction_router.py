"""
Plutus Backend - Transaction Router (Simplified)
API endpoints for money transfer and transaction history only.

Team: Yay!
Date: August 30, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any

from ..schemas.transaction_schemas import (
    SendMoneyRequest
)
from ..services import get_transaction_service, TransactionService
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/transactions", tags=["Money Transfer"])
logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/send/{user_id}", status_code=status.HTTP_201_CREATED)
async def send_money(
    user_id: str,
    transaction_data: SendMoneyRequest,
    request: Request,
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Send money to another user with simplified response.
    
    Returns: transaction_id, from_user_id, to_user_id, amount, description, timestamp
    """
    try:
        logger.info(f"Money transfer requested by user {user_id}: PKR {transaction_data.amount}")
        
        result = await transaction_service.send_money(user_id, transaction_data)
        
        if not result.get("success"):
            error_code = result.get("error_code", "INTERNAL_ERROR")
            status_code = status.HTTP_400_BAD_REQUEST
            
            if error_code == "INSUFFICIENT_BALANCE":
                status_code = status.HTTP_402_PAYMENT_REQUIRED
            elif error_code in ["USER_NOT_FOUND", "RECIPIENT_NOT_FOUND"]:
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail=result.get("message", "Transaction failed")
            )
        
        logger.info(f"Money transfer completed by user {user_id}: PKR {transaction_data.amount}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Money transfer error for user {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction failed due to internal error"
        )


@router.get("/history/{user_id}")
async def get_transaction_history(
    user_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get transaction history with simplified response.
    
    Returns: List of transactions with transaction_id, from_user_id, to_user_id, amount, description, timestamp
    """
    try:
        logger.info(f"Transaction history requested by user {user_id}")
        
        result = await transaction_service.get_transaction_history(user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to retrieve transaction history")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transaction history error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )
