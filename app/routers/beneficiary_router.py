"""
Plutus Backend - Beneficiary Router (Simplified)
API endpoints for essential beneficiary management: add, list, search, remove.
Returns simplified responses without wrapper structure.

Team: Yay!
Date: August 30, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any

from ..schemas.beneficiary_schemas import BeneficiaryAddRequest
from ..services import get_beneficiary_service, BeneficiaryService
from ..core.logging import get_logger

# Create router
router = APIRouter(prefix="/beneficiaries", tags=["Beneficiary Management"])
logger = get_logger(__name__)


@router.post("/add/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_beneficiary(
    user_id: str,
    beneficiary_data: BeneficiaryAddRequest,
    request: Request,
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Add a new beneficiary for the user.
    URL: /api/beneficiaries/add/{user_id}
    
    Returns simplified: owner_user_id, beneficiary_id, name, account_number
    """
    try:
        logger.info(f"Add beneficiary requested by user {user_id}: {beneficiary_data.name}")
        
        result = await beneficiary_service.add_beneficiary(user_id, beneficiary_data)
        
        # Check for error in simplified response
        if "error" in result:
            # Determine appropriate status code based on error message
            error_msg = result["error"]
            if "already exists" in error_msg.lower():
                status_code = status.HTTP_409_CONFLICT
            else:
                status_code = status.HTTP_400_BAD_REQUEST
            
            raise HTTPException(
                status_code=status_code,
                detail=error_msg
            )
        
        logger.info(f"Beneficiary added successfully by user {user_id}: {beneficiary_data.name}")
        return result  # Return simplified response directly
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add beneficiary error for user {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add beneficiary due to internal error"
        )


@router.get("/list/{user_id}")
async def list_beneficiaries(
    user_id: str,
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    List all beneficiaries for the user.
    URL: /api/beneficiaries/list/{user_id}
    
    Returns simplified: {"beneficiaries": [{"beneficiary_id", "name", "account_number"}]}
    """
    try:
        logger.info(f"List beneficiaries requested by user {user_id}")
        
        result = await beneficiary_service.list_beneficiaries(user_id)
        
        # Check for error in simplified response
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result  # Return simplified response directly
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List beneficiaries error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve beneficiaries"
        )


@router.get("/search/{user_id}/{query}")
async def search_beneficiaries(
    user_id: str,
    query: str,
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Search beneficiaries by name for the user.
    URL: /api/beneficiaries/search/{user_id}/{query}
    
    Returns simplified: {"query", "matches", "total_matches"}
    """
    try:
        logger.info(f"Search beneficiaries requested by user {user_id}: {query}")
        
        result = await beneficiary_service.search_beneficiaries(user_id, query)
        
        # Check for error in simplified response
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result  # Return simplified response directly
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search beneficiaries error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search beneficiaries"
        )


@router.delete("/remove/{user_id}/{beneficiary_id}")
async def remove_beneficiary(
    user_id: str,
    beneficiary_id: str,
    request: Request,
    beneficiary_service: BeneficiaryService = Depends(get_beneficiary_service)
) -> Dict[str, Any]:
    """
    Remove a beneficiary from the user's list.
    URL: /api/beneficiaries/remove/{user_id}/{beneficiary_id}
    
    Returns simplified: {"beneficiary_id", "name"}
    """
    try:
        logger.info(f"Remove beneficiary requested by user {user_id}: {beneficiary_id}")
        
        result = await beneficiary_service.remove_beneficiary(user_id, beneficiary_id)
        
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
        
        logger.info(f"Beneficiary removed successfully by user {user_id}: {beneficiary_id}")
        return result  # Return simplified response directly
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove beneficiary error for user {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove beneficiary due to internal error"
        )
