"""
Plutus Backend - Transaction Router
API endpoints for money transfer operations: send money, transaction history, status.

Team: Yay!
Date: August 29, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ..schemas.transaction_schemas import (
    TransactionRequest,
    TransactionHistoryRequest,
    TransactionStatusRequest
)
from ..services import get_transaction_service, TransactionService
from ..core.security import get_security_manager
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/transactions", tags=["Money Transfer"])
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


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_money(
    transaction_data: TransactionRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Send money to a beneficiary.
    
    - **beneficiary_id**: ID of the beneficiary to send money to
    - **amount**: Amount to send (minimum PKR 100, maximum PKR 500,000)
    - **description**: Optional description for the transaction
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"Money transfer requested by user {user_id}: PKR {transaction_data.amount}")
        
        result = await transaction_service.send_money(
            user_id,
            transaction_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if not result["success"]:
            # Map error codes to appropriate HTTP status codes
            status_code = status.HTTP_400_BAD_REQUEST
            
            if result["error_code"] == "INSUFFICIENT_BALANCE":
                status_code = status.HTTP_402_PAYMENT_REQUIRED
            elif result["error_code"] == "BENEFICIARY_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            elif result["error_code"] == "DAILY_LIMIT_EXCEEDED":
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif result["error_code"] == "USER_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": result["message"],
                    "error_code": result["error_code"]
                }
            )
        
        logger.info(f"Money transfer completed by user {user_id}: PKR {transaction_data.amount}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Money transfer error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Transaction failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/history")
async def get_transaction_history(
    history_request: TransactionHistoryRequest,
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get transaction history for the authenticated user with filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status_filter**: Filter by transaction status (completed/processing/failed)
    - **start_date**: Filter from date (YYYY-MM-DD)
    - **end_date**: Filter to date (YYYY-MM-DD)
    - **beneficiary_name**: Filter by beneficiary name
    """
    try:
        logger.info(f"Transaction history requested by user {user_id}")
        
        result = await transaction_service.get_transaction_history(
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
        logger.error(f"Transaction history error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve transaction history",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/history")
async def get_transaction_history_get(
    page: int = 1,
    page_size: int = 20,
    status_filter: str = None,
    start_date: str = None,
    end_date: str = None,
    beneficiary_name: str = None,
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get transaction history (alternative GET endpoint).
    
    Query parameters:
    - **page**: Page number
    - **page_size**: Items per page
    - **status_filter**: Filter by status
    - **start_date**: Filter from date
    - **end_date**: Filter to date
    - **beneficiary_name**: Filter by beneficiary
    """
    try:
        history_request = TransactionHistoryRequest(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            beneficiary_name=beneficiary_name
        )
        
        return await get_transaction_history(history_request, user_id, transaction_service)
        
    except Exception as e:
        logger.error(f"Transaction history GET error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve transaction history",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/status")
async def get_transaction_status(
    status_request: TransactionStatusRequest,
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get status of a specific transaction.
    
    - **transaction_id**: ID of the transaction to check
    """
    try:
        logger.info(f"Transaction status requested by user {user_id}: {status_request.transaction_id}")
        
        result = await transaction_service.get_transaction_status(
            user_id,
            status_request
        )
        
        if not result["success"]:
            status_code = status.HTTP_400_BAD_REQUEST
            if result["error_code"] == "TRANSACTION_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": result["message"],
                    "error_code": result["error_code"]
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transaction status error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve transaction status",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/status/{transaction_id}")
async def get_transaction_status_get(
    transaction_id: str,
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get status of a specific transaction (alternative GET endpoint).
    """
    try:
        status_request = TransactionStatusRequest(transaction_id=transaction_id)
        
        return await get_transaction_status(status_request, user_id, transaction_service)
        
    except Exception as e:
        logger.error(f"Transaction status GET error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve transaction status",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/limits")
async def get_daily_limits(
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get current daily transfer limits and remaining amounts for the user.
    
    Returns daily limits, used amounts, and remaining capacity.
    """
    try:
        logger.info(f"Daily limits requested by user {user_id}")
        
        # Check daily limits with zero amount to get current status
        limit_check = await transaction_service.check_daily_transfer_limit(user_id, 0)
        
        return {
            "success": True,
            "message": "Daily limits retrieved successfully",
            "data": {
                "remaining_amount": limit_check["remaining_amount"],
                "remaining_transactions": limit_check["remaining_transactions"],
                "daily_transfer_limit": 500000.0,  # From settings
                "daily_transaction_limit": 10,     # From settings
                "min_transfer_amount": 100.0,      # From settings
                "max_transfer_amount": 500000.0    # From settings
            }
        }
        
    except Exception as e:
        logger.error(f"Daily limits error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve daily limits",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/recent")
async def get_recent_transactions(
    limit: int = 5,
    user_id: str = Depends(get_current_user_id),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Dict[str, Any]:
    """
    Get recent transactions for quick overview.
    
    Query parameters:
    - **limit**: Number of recent transactions to return (max: 20)
    """
    try:
        # Validate limit
        if limit > 20:
            limit = 20
        if limit < 1:
            limit = 5
        
        logger.info(f"Recent transactions requested by user {user_id}")
        
        history_request = TransactionHistoryRequest(
            page=1,
            page_size=limit
        )
        
        result = await transaction_service.get_transaction_history(
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
        
        return {
            "success": True,
            "message": "Recent transactions retrieved successfully",
            "data": {
                "transactions": result["data"]["data"],
                "count": len(result["data"]["data"]),
                "total_sent_today": result["data"]["summary"]["total_sent"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recent transactions error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve recent transactions",
                "error_code": "INTERNAL_ERROR"
            }
        )
