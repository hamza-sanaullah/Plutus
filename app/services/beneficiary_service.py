"""
Plutus Backend - Beneficiary Management Service
Handles beneficiary operations: add, list, update, remove, search.

Team: Yay!
Date: August 29, 2025
"""

from typing import Dict, Any, Optional, List
import pandas as pd

from .base_service import BaseService
from ..schemas.beneficiary_schemas import (
    BeneficiaryAddRequest,
    BeneficiaryListRequest,
    BeneficiaryUpdateRequest,
    BeneficiarySearchRequest
)


class BeneficiaryService(BaseService):
    """
    Beneficiary management service for all beneficiary-related operations.
    """
    
    async def add_beneficiary(
        self,
        user_id: str,
        beneficiary_data: BeneficiaryAddRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new beneficiary for the user.
        """
        try:
            # Validate user exists
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            # Validate beneficiary account details
            account_validation = self.security.validate_beneficiary_account(
                beneficiary_data.account_number,
                beneficiary_data.bank_name
            )
            
            if not account_validation["valid"]:
                return self.create_error_response(
                    f"Invalid beneficiary details: {', '.join(account_validation['errors'])}",
                    "INVALID_BENEFICIARY"
                )
            
            # Check if beneficiary already exists for this user
            existing_beneficiary = await self.find_beneficiary_by_name(user_id, beneficiary_data.name)
            if existing_beneficiary:
                return self.create_error_response(
                    f"Beneficiary '{beneficiary_data.name}' already exists",
                    "BENEFICIARY_EXISTS"
                )
            
            # Check if same account number already exists for this user
            existing_account = await self.find_beneficiary_by_account(user_id, beneficiary_data.account_number)
            if existing_account:
                return self.create_error_response(
                    f"Account number already exists for beneficiary: {existing_account['name']}",
                    "ACCOUNT_EXISTS"
                )
            
            # Generate beneficiary ID
            beneficiary_id = self.security.generate_beneficiary_id()
            
            # Create beneficiary data
            beneficiary_record = {
                "owner_user_id": user_id,
                "beneficiary_id": beneficiary_id,
                "name": beneficiary_data.name,
                "bank_name": beneficiary_data.bank_name,
                "account_number": beneficiary_data.account_number,
                "added_at": self.create_timestamp()
            }
            
            # Save beneficiary to CSV
            success = await self.storage.append_csv(
                self.settings.beneficiaries_csv,
                beneficiary_record
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to add beneficiary",
                    "ADD_FAILED"
                )
            
            # Log beneficiary addition
            await self.log_audit(
                user_id=user_id,
                action="beneficiary_added",
                details={
                    "beneficiary_id": beneficiary_id,
                    "name": beneficiary_data.name,
                    "bank_name": beneficiary_data.bank_name,
                    "account_number": beneficiary_data.account_number
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Beneficiary added for user {user_id}: {beneficiary_data.name}")
            
            return self.create_success_response(
                "Beneficiary added successfully",
                {
                    "beneficiary_id": beneficiary_id,
                    "name": beneficiary_data.name,
                    "bank_name": beneficiary_data.bank_name,
                    "account_number": beneficiary_data.account_number,
                    "added_at": beneficiary_record["added_at"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add beneficiary for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to add beneficiary due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def list_beneficiaries(
        self,
        user_id: str,
        list_request: BeneficiaryListRequest
    ) -> Dict[str, Any]:
        """
        List beneficiaries for a user with filtering and pagination.
        """
        try:
            # Get beneficiaries CSV
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return self.create_success_response(
                    "Beneficiaries retrieved successfully",
                    {
                        "data": [],
                        "pagination": {
                            "current_page": 1,
                            "page_size": list_request.page_size,
                            "total_items": 0,
                            "total_pages": 0,
                            "has_next": False,
                            "has_previous": False
                        }
                    }
                )
            
            # Filter by user
            user_beneficiaries = beneficiaries_df[
                beneficiaries_df['owner_user_id'] == user_id
            ].copy()
            
            # Apply search filter
            if list_request.search_name:
                user_beneficiaries = user_beneficiaries[
                    user_beneficiaries['name'].str.contains(
                        list_request.search_name, case=False, na=False
                    )
                ]
            
            # Apply bank filter
            if list_request.bank_filter:
                user_beneficiaries = user_beneficiaries[
                    user_beneficiaries['bank_name'].str.contains(
                        list_request.bank_filter, case=False, na=False
                    )
                ]
            
            # Sort by added date (newest first)
            user_beneficiaries = user_beneficiaries.sort_values('added_at', ascending=False)
            
            # Pagination
            total_items = len(user_beneficiaries)
            start_idx = (list_request.page - 1) * list_request.page_size
            end_idx = start_idx + list_request.page_size
            
            paginated_beneficiaries = user_beneficiaries.iloc[start_idx:end_idx]
            
            # Format beneficiaries
            beneficiaries = []
            for _, row in paginated_beneficiaries.iterrows():
                beneficiaries.append({
                    "beneficiary_id": row['beneficiary_id'],
                    "name": row['name'],
                    "bank_name": row['bank_name'],
                    "account_number": row['account_number'],
                    "added_at": row['added_at']
                })
            
            # Pagination info
            total_pages = (total_items + list_request.page_size - 1) // list_request.page_size
            
            pagination = {
                "current_page": list_request.page,
                "page_size": list_request.page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": list_request.page < total_pages,
                "has_previous": list_request.page > 1
            }
            
            return self.create_success_response(
                "Beneficiaries retrieved successfully",
                {
                    "data": beneficiaries,
                    "pagination": pagination
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to list beneficiaries for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve beneficiaries",
                "INTERNAL_ERROR"
            )
    
    async def remove_beneficiary(
        self,
        user_id: str,
        beneficiary_id: str,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Remove a beneficiary for the user.
        """
        try:
            # Find beneficiary
            beneficiary = await self.get_beneficiary_by_id(user_id, beneficiary_id)
            if not beneficiary:
                return self.create_error_response(
                    "Beneficiary not found",
                    "BENEFICIARY_NOT_FOUND"
                )
            
            # Remove beneficiary from CSV
            success = await self.storage.delete_row(
                self.settings.beneficiaries_csv,
                {
                    "owner_user_id": user_id,
                    "beneficiary_id": beneficiary_id
                }
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to remove beneficiary",
                    "REMOVE_FAILED"
                )
            
            # Log beneficiary removal
            await self.log_audit(
                user_id=user_id,
                action="beneficiary_removed",
                details={
                    "beneficiary_id": beneficiary_id,
                    "name": beneficiary['name'],
                    "bank_name": beneficiary['bank_name'],
                    "account_number": beneficiary['account_number']
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Beneficiary removed for user {user_id}: {beneficiary['name']}")
            
            return self.create_success_response(
                "Beneficiary removed successfully",
                {
                    "beneficiary_id": beneficiary_id,
                    "name": beneficiary['name'],
                    "removed_at": self.create_timestamp()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to remove beneficiary {beneficiary_id} for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to remove beneficiary due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def update_beneficiary(
        self,
        user_id: str,
        beneficiary_id: str,
        update_data: BeneficiaryUpdateRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update beneficiary details.
        """
        try:
            # Find existing beneficiary
            beneficiary = await self.get_beneficiary_by_id(user_id, beneficiary_id)
            if not beneficiary:
                return self.create_error_response(
                    "Beneficiary not found",
                    "BENEFICIARY_NOT_FOUND"
                )
            
            # Prepare update data
            updates = {}
            
            if update_data.name is not None:
                # Check if new name conflicts with existing beneficiary
                existing = await self.find_beneficiary_by_name(user_id, update_data.name)
                if existing and existing['beneficiary_id'] != beneficiary_id:
                    return self.create_error_response(
                        f"Beneficiary name '{update_data.name}' already exists",
                        "NAME_EXISTS"
                    )
                updates["name"] = update_data.name
            
            if update_data.bank_name is not None:
                updates["bank_name"] = update_data.bank_name
            
            if update_data.account_number is not None:
                # Validate account number
                account_validation = self.security.validate_account_number(update_data.account_number)
                if not account_validation["valid"]:
                    return self.create_error_response(
                        f"Invalid account number: {', '.join(account_validation['errors'])}",
                        "INVALID_ACCOUNT"
                    )
                
                # Check if account number conflicts with existing beneficiary
                existing = await self.find_beneficiary_by_account(user_id, update_data.account_number)
                if existing and existing['beneficiary_id'] != beneficiary_id:
                    return self.create_error_response(
                        f"Account number already exists for beneficiary: {existing['name']}",
                        "ACCOUNT_EXISTS"
                    )
                
                updates["account_number"] = account_validation["formatted_number"]
            
            if not updates:
                return self.create_error_response(
                    "No valid updates provided",
                    "NO_UPDATES"
                )
            
            # Update beneficiary
            success = await self.storage.update_row(
                self.settings.beneficiaries_csv,
                {
                    "owner_user_id": user_id,
                    "beneficiary_id": beneficiary_id
                },
                updates
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to update beneficiary",
                    "UPDATE_FAILED"
                )
            
            # Get updated beneficiary data
            updated_beneficiary = await self.get_beneficiary_by_id(user_id, beneficiary_id)
            
            # Log beneficiary update
            await self.log_audit(
                user_id=user_id,
                action="beneficiary_updated",
                details={
                    "beneficiary_id": beneficiary_id,
                    "updates": updates,
                    "previous_data": beneficiary
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Beneficiary updated for user {user_id}: {beneficiary_id}")
            
            return self.create_success_response(
                "Beneficiary updated successfully",
                {
                    "beneficiary_id": beneficiary_id,
                    "name": updated_beneficiary['name'],
                    "bank_name": updated_beneficiary['bank_name'],
                    "account_number": updated_beneficiary['account_number'],
                    "updated_at": self.create_timestamp()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update beneficiary {beneficiary_id} for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to update beneficiary due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def search_beneficiaries(
        self,
        user_id: str,
        search_request: BeneficiarySearchRequest
    ) -> Dict[str, Any]:
        """
        Search beneficiaries by name.
        """
        try:
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return self.create_success_response(
                    "Search completed",
                    {
                        "query": search_request.query,
                        "matches": [],
                        "total_matches": 0
                    }
                )
            
            # Filter by user
            user_beneficiaries = beneficiaries_df[
                beneficiaries_df['owner_user_id'] == user_id
            ]
            
            # Search by name
            if search_request.exact_match:
                matches = user_beneficiaries[
                    user_beneficiaries['name'].str.lower() == search_request.query.lower()
                ]
            else:
                matches = user_beneficiaries[
                    user_beneficiaries['name'].str.contains(
                        search_request.query, case=False, na=False
                    )
                ]
            
            # Format matches
            match_list = []
            for _, row in matches.iterrows():
                match_list.append({
                    "beneficiary_id": row['beneficiary_id'],
                    "name": row['name'],
                    "bank_name": row['bank_name'],
                    "account_number": row['account_number']
                })
            
            return self.create_success_response(
                "Search completed",
                {
                    "query": search_request.query,
                    "matches": match_list,
                    "total_matches": len(match_list)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to search beneficiaries for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Search failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def find_beneficiary_by_name(self, user_id: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Find beneficiary by name for a specific user.
        """
        try:
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return None
            
            matches = beneficiaries_df[
                (beneficiaries_df['owner_user_id'] == user_id) &
                (beneficiaries_df['name'].str.lower() == name.lower())
            ]
            
            if matches.empty:
                return None
            
            return matches.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to find beneficiary by name {name} for user {user_id}: {str(e)}")
            return None
    
    async def find_beneficiary_by_account(self, user_id: str, account_number: str) -> Optional[Dict[str, Any]]:
        """
        Find beneficiary by account number for a specific user.
        """
        try:
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return None
            
            matches = beneficiaries_df[
                (beneficiaries_df['owner_user_id'] == user_id) &
                (beneficiaries_df['account_number'] == account_number)
            ]
            
            if matches.empty:
                return None
            
            return matches.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to find beneficiary by account {account_number} for user {user_id}: {str(e)}")
            return None
    
    async def get_beneficiary_by_id(self, user_id: str, beneficiary_id: str) -> Optional[Dict[str, Any]]:
        """
        Get beneficiary by ID for a specific user.
        """
        try:
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return None
            
            matches = beneficiaries_df[
                (beneficiaries_df['owner_user_id'] == user_id) &
                (beneficiaries_df['beneficiary_id'] == beneficiary_id)
            ]
            
            if matches.empty:
                return None
            
            return matches.iloc[0].to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to get beneficiary {beneficiary_id} for user {user_id}: {str(e)}")
            return None


# Global instance
beneficiary_service = BeneficiaryService()


def get_beneficiary_service() -> BeneficiaryService:
    """
    Dependency to get beneficiary service instance.
    """
    return beneficiary_service
