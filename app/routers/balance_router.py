"""
Plutus Backend - Balance Router (Simplified)
API endpoint for balance checking only.

Team: Yay!
Date: August 30, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ..services import get_balance_service, BalanceService
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/balance", tags=["Balance Management"])
logger = get_logger(__name__)


@router.get("/check/{user_id}")
async def check_balance(
    user_id: str,
    balance_service: BalanceService = Depends(get_balance_service)
) -> Dict[str, Any]:
    """
    Check user balance with simplified response.
    
    Returns: user_id, account_number, balance only
    """
    try:
        logger.info(f"Balance check requested for user: {user_id}")
        
        result = await balance_service.check_balance(user_id)
        
        # Check for error in simplified response
        if "error" in result:
            error_msg = result["error"]
            if "not found" in error_msg.lower():
                status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_400_BAD_REQUEST
            
            raise HTTPException(
                status_code=status_code,
                detail=error_msg
            )
        
        return result  # Return simplified response directly
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Balance check error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve balance"
        )
