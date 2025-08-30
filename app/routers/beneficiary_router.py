"""
Plutus Backend - Beneficiary Router
API endpoints for beneficiary management: add, list, update, remove, search.

Team: Yay!
Date: August 29, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ..schemas.beneficiary_schemas import (
    BeneficiaryAddRequest,
    BeneficiaryListRequest,
    BeneficiaryUpdateRequest,
    BeneficiarySearchRequest
)
from ..services import get_beneficiary_service, BeneficiaryService
from ..core.security import get_security_manager
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/beneficiaries", tags=["Beneficiary Management"])
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
            detail="Invalid or expired token"
        )
    
    return token_payload["user_id"]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_beneficiary(
    beneficiary_data: BeneficiaryAddRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Add a new beneficiary for the authenticated user.
    
    - **name**: Beneficiary's full name
    - **bank_name**: Bank name (HBL, UBL, MCB, etc.)
    - **account_number**: Valid Pakistani bank account number
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"Add beneficiary requested by user {user_id}: {beneficiary_data.name}")
        
        result = await beneficiary_service.add_beneficiary(
            user_id,
            beneficiary_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        logger.info(f"Beneficiary added successfully by user {user_id}: {beneficiary_data.name}")
        
        # Add success field for backward compatibility with tests
        result["success"] = True
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add beneficiary error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add beneficiary"
        )


@router.post("/list")
async def list_beneficiaries(
    list_request: BeneficiaryListRequest,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    List beneficiaries for the authenticated user with filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **search_name**: Filter by beneficiary name
    - **bank_filter**: Filter by bank name
    """
    try:
        logger.info(f"List beneficiaries requested by user {user_id}")
        
        result = await beneficiary_service.list_beneficiaries(
            user_id,
            list_request
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        result["success"] = True
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List beneficiaries error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve beneficiaries"
        )


@router.get("/")
async def get_all_beneficiaries(
    page: int = 1,
    page_size: int = 20,
    search_name: str = None,
    bank_filter: str = None,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Get all beneficiaries for the authenticated user (alternative GET endpoint).
    
    Query parameters:
    - **page**: Page number
    - **page_size**: Items per page
    - **search_name**: Filter by beneficiary name
    - **bank_filter**: Filter by bank name
    """
    try:
        list_request = BeneficiaryListRequest(
            page=page,
            page_size=page_size,
            search_name=search_name,
            bank_filter=bank_filter
        )
        
        return await list_beneficiaries(list_request, user_id, beneficiary_service)
        
    except Exception as e:
        logger.error(f"Get beneficiaries error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve beneficiaries"
        )


@router.put("/{beneficiary_id}")
async def update_beneficiary(
    beneficiary_id: str,
    update_data: BeneficiaryUpdateRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Update an existing beneficiary's details.
    
    - **name**: New beneficiary name (optional)
    - **bank_name**: New bank name (optional)
    - **account_number**: New account number (optional)
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"Update beneficiary requested by user {user_id}: {beneficiary_id}")
        
        result = await beneficiary_service.update_beneficiary(
            user_id,
            beneficiary_id,
            update_data,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            status_code = status.HTTP_400_BAD_REQUEST
            if result.get("error_code") == "BENEFICIARY_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
        
        logger.info(f"Beneficiary updated successfully by user {user_id}: {beneficiary_id}")
        result["success"] = True
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update beneficiary error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update beneficiary"
        )


@router.delete("/{beneficiary_id}")
async def remove_beneficiary(
    beneficiary_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Remove a beneficiary from the user's list.
    
    This action cannot be undone.
    """
    try:
        client_ip = get_client_ip(request)
        request_id = request.headers.get("X-Request-ID")
        
        logger.info(f"Remove beneficiary requested by user {user_id}: {beneficiary_id}")
        
        result = await beneficiary_service.remove_beneficiary(
            user_id,
            beneficiary_id,
            ip_address=client_ip,
            request_id=request_id
        )
        
        if result["status"] != "success":
            status_code = status.HTTP_400_BAD_REQUEST
            if result.get("error_code") == "BENEFICIARY_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
        
        logger.info(f"Beneficiary removed successfully by user {user_id}: {beneficiary_id}")
        result["success"] = True
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove beneficiary error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove beneficiary"
        )


@router.post("/search")
async def search_beneficiaries(
    search_request: BeneficiarySearchRequest,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Search beneficiaries by name.
    
    - **query**: Search term
    - **exact_match**: Whether to match exactly (default: false)
    """
    try:
        logger.info(f"Search beneficiaries requested by user {user_id}: {search_request.query}")
        
        result = await beneficiary_service.search_beneficiaries(
            user_id,
            search_request
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        result["success"] = True
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search beneficiaries error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search beneficiaries"
        )


@router.get("/{beneficiary_id}")
async def get_beneficiary(
    beneficiary_id: str,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Get a single beneficiary by ID.
    """
    try:
        logger.info(f"Get beneficiary requested by user {user_id}: {beneficiary_id}")
        
        result = await beneficiary_service.get_beneficiary(user_id, beneficiary_id)
        
        if result["status"] != "success":
            status_code = status.HTTP_400_BAD_REQUEST
            if result.get("error_code") == "BENEFICIARY_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
        
        result["success"] = True
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get beneficiary error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve beneficiary"
        )


@router.get("/search/{query}")
async def search_beneficiaries_get(
    query: str,
    exact_match: bool = False,
    user_id: str = Depends(get_current_user_id),
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Search beneficiaries by name (alternative GET endpoint).
    
    Query parameters:
    - **exact_match**: Whether to match exactly
    """
    try:
        search_request = BeneficiarySearchRequest(
            query=query,
            exact_match=exact_match
        )
        
        return await search_beneficiaries(search_request, user_id, beneficiary_service)
        
    except Exception as e:
        logger.error(f"Search beneficiaries GET error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search beneficiaries"
        )
