"""
Plutus Backend - Balance Router
API endpoints for balance operations: check balance, deposit, withdraw, history.

Team: Yay!
Date: August 29, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ..schemas.balance_schemas import (
    DepositRequest,
    WithdrawRequest,
    BalanceHistoryRequest
)
from ..services import get_balance_service, BalanceService
from ..core.security import get_security_manager
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/balance", tags=["Balance Management"])
security = HTTPBearer()
logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token."""
    security_manager = get_security_manager()
    token_payload = security_manager.verify_access_token(credentials.credentials)
    
    if not token_payload["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid or expired token",
                "error_code": "INVALID_TOKEN"
            }
        )
    
    return token_payload["user_id"]


@router.get("/current")
async def get_current_balance(
    user_id: str = Depends(get_current_user_id),
    balance_service: BalanceService = Depends(get_balance_service)
) -> Dict[str, Any]:
    """
    Get current account balance for the authenticated user.
    
    Returns current balance and account information.
    """
    try:
        logger.info(f"Balance check requested by user: {user_id}")
        
        result = await balance_service.check_balance(user_id)
        
        if not result["status"] == "success":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": result["message"],
                    "error_code": "BALANCE_ERROR"
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Balance check error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve balance",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/deposit")
async def deposit_money(
    deposit_data: DepositRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    balance_service: BalanceService = Depends(get_balance_service)
) -> Dict[str, Any]:
    """
    Deposit money into the user's account.
    
    - **amount**: Amount to deposit (minimum PKR 100)
    - **description**: Optional description for the deposit
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"Deposit requested by user {user_id}: PKR {deposit_data.amount}")
        
        result = await balance_service.deposit_money(
            user_id,
            deposit_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": result["message"],
                    "error_code": result["error_code"]
                }
            )
        
        logger.info(f"Deposit completed for user {user_id}: PKR {deposit_data.amount}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deposit error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Deposit failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/withdraw")
async def withdraw_money(
    withdraw_data: WithdrawRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    balance_service: BalanceService = Depends(get_balance_service)
) -> Dict[str, Any]:
    """
    Withdraw money from the user's account.
    
    - **amount**: Amount to withdraw (minimum PKR 100)
    - **description**: Optional description for the withdrawal
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"Withdrawal requested by user {user_id}: PKR {withdraw_data.amount}")
        
        result = await balance_service.withdraw_money(
            user_id,
            withdraw_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if not result["success"]:
            status_code = status.HTTP_400_BAD_REQUEST
            if result["error_code"] == "INSUFFICIENT_BALANCE":
                status_code = status.HTTP_402_PAYMENT_REQUIRED
            
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": result["message"],
                    "error_code": result["error_code"]
                }
            )
        
        logger.info(f"Withdrawal completed for user {user_id}: PKR {withdraw_data.amount}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Withdrawal error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Withdrawal failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/history")
async def get_balance_history(
    history_request: BalanceHistoryRequest,
    user_id: str = Depends(get_current_user_id),
    balance_service: BalanceService = Depends(get_balance_service)
) -> Dict[str, Any]:
    """
    Get balance transaction history with filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **transaction_type**: Filter by type (deposit/withdrawal)
    - **start_date**: Filter from date (YYYY-MM-DD)
    - **end_date**: Filter to date (YYYY-MM-DD)
    """
    try:
        logger.info(f"Balance history requested by user {user_id}")
        
        result = await balance_service.get_balance_history(
            user_id,
            history_request
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": result["message"],
                    "error_code": result["error_code"]
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Balance history error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve balance history",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/summary")
async def get_balance_summary(
    user_id: str = Depends(get_current_user_id),
    balance_service: BalanceService = Depends(get_balance_service)
) -> Dict[str, Any]:
    """
    Get balance summary including current balance and recent activity.
    
    Returns balance, recent transactions, and daily limits.
    """
    try:
        logger.info(f"Balance summary requested by user {user_id}")
        
        # Get current balance
        balance_result = await balance_service.check_balance(user_id)
        
        if not balance_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": balance_result["message"],
                    "error_code": balance_result["error_code"]
                }
            )
        
        # Get recent history (last 5 transactions)
        history_request = BalanceHistoryRequest(page=1, page_size=5)
        history_result = await balance_service.get_balance_history(
            user_id,
            history_request
        )
        
        recent_transactions = []
        if history_result["success"]:
            recent_transactions = history_result["data"]["data"]
        
        return {
            "success": True,
            "message": "Balance summary retrieved successfully",
            "data": {
                "current_balance": balance_result["data"]["balance"],
                "account_number": balance_result["data"]["account_number"],
                "bank_name": balance_result["data"]["bank_name"],
                "recent_transactions": recent_transactions,
                "daily_limits": balance_result["data"].get("daily_limits", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Balance summary error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve balance summary",
                "error_code": "INTERNAL_ERROR"
            }
        )
