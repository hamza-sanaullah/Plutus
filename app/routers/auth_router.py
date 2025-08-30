"""
Plutus Backend - Authentication Router
API endpoints for user authentication: register, login, refresh tokens.

Team: Yay!
Date: August 29, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ..schemas.auth_schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    RefreshTokenRequest
)
from ..services import get_auth_service, AuthService
from ..core.security import get_security_manager
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistrationRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Register a new user account.
    
    - **full_name**: Complete name of the user
    - **email**: Valid email address  
    - **phone_number**: Pakistani phone number (+92)
    - **account_number**: User-provided bank account number
    - **bank_name**: Name of the bank
    - **password**: Strong password (min 8 chars)
    - **confirm_password**: Password confirmation
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"User registration attempt: {user_data.username}")
        
        result = await auth_service.register_user(
            user_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": result["message"],
                    "error_code": result.get("error_code")
                }
            )
        
        logger.info(f"User registered successfully: {user_data.username}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Registration failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/login")
async def login_user(
    login_data: UserLoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Authenticate user and return access tokens.
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"User login attempt: {login_data.username}")
        
        result = await auth_service.login_user(
            login_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": result["message"],
                    "error_code": result.get("error_code")
                }
            )
        
        logger.info(f"User logged in successfully: {login_data.username}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Login failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/refresh")
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info("Token refresh attempt")
        
        result = await auth_service.refresh_token(
            refresh_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": result["message"],
                    "error_code": result.get("error_code")
                }
            )
        
        logger.info("Token refreshed successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Token refresh failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/logout")
async def logout_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Logout user and invalidate tokens.
    
    Requires valid access token in Authorization header.
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        # Verify token and get user info
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
        
        user_id = token_payload["user_id"]
        logger.info(f"User logout attempt: {user_id}")
        
        result = await auth_service.logout_user(
            user_id,
            credentials.credentials,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": result["message"],
                    "error_code": result.get("error_code")
                }
            )
        
        logger.info(f"User logged out successfully: {user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Logout failed due to internal error",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/profile")
async def get_user_profile(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Get current user's profile information.
    
    Requires valid access token in Authorization header.
    """
    try:
        # Verify token and get user info
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
        
        user_id = token_payload["user_id"]
        
        result = await auth_service.get_user_profile(user_id)
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": result["message"],
                    "error_code": result.get("error_code")
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to retrieve profile",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify if the provided access token is valid.
    
    Requires access token in Authorization header.
    """
    try:
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
        
        return {
            "status": "success",
            "message": "Token is valid",
            "data": {
                "user_id": token_payload["user_id"],
                "email": token_payload["email"],
                "expires_at": token_payload["exp"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Token verification failed",
                "error_code": "INTERNAL_ERROR"
            }
        )
