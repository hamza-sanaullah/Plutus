"""
Plutus Backend - Beneficiary Management Service (Simplified)
Handles only essential beneficiary operations: add, list, search, remove.
Returns simplified responses without wrapper structure.

Team: Yay!
Date: August 30, 2025
"""

from typing import Dict, Any
import pandas as pd
from datetime import datetime

from .base_service import BaseService
from ..schemas.beneficiary_schemas import BeneficiaryAddRequest


class BeneficiaryService(BaseService):
    """
    Simplified beneficiary service for essential operations only.
    Returns clean, simplified responses.
    """
    
    async def add_beneficiary(
        self,
        user_id: str,
        beneficiary_data: BeneficiaryAddRequest
    ) -> Dict[str, Any]:
        """
        Add a new beneficiary for the user.
        Returns simplified response without wrapper structure.
        """
        try:
            # Read existing beneficiaries
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            # Check if beneficiary name already exists for this user
            if not beneficiaries_df.empty:
                existing = beneficiaries_df[
                    (beneficiaries_df['owner_user_id'] == user_id) &
                    (beneficiaries_df['name'].str.lower() == beneficiary_data.name.lower())
                ]
                if not existing.empty:
                    return {"error": f"Beneficiary '{beneficiary_data.name}' already exists"}
                
                # Check if account number already exists for this user
                existing_account = beneficiaries_df[
                    (beneficiaries_df['owner_user_id'] == user_id) &
                    (beneficiaries_df['account_number'] == beneficiary_data.account_number)
                ]
                if not existing_account.empty:
                    return {"error": "Account number already exists"}
            
            # Generate beneficiary ID
            beneficiary_id = f"BEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create beneficiary record for CSV (includes added_at)
            beneficiary_record = {
                'owner_user_id': user_id,
                'beneficiary_id': beneficiary_id,
                'name': beneficiary_data.name,
                'account_number': beneficiary_data.account_number,
                'added_at': datetime.now().isoformat()
            }
            
            # Save beneficiary to CSV
            import os
            csv_path = os.path.join('data', 'beneficiaries.csv')
            
            try:
                beneficiaries_df = pd.read_csv(csv_path)
            except:
                beneficiaries_df = pd.DataFrame(columns=['owner_user_id', 'beneficiary_id', 'name', 'account_number', 'added_at'])
            
            new_beneficiary = pd.DataFrame([beneficiary_record])
            beneficiaries_df = pd.concat([beneficiaries_df, new_beneficiary], ignore_index=True)
            beneficiaries_df.to_csv(csv_path, index=False)
            
            self.logger.info(f"Beneficiary added for user {user_id}: {beneficiary_data.name}")
            
            # Return simplified response (no added_at field)
            return {
                "owner_user_id": user_id,
                "beneficiary_id": beneficiary_id,
                "name": beneficiary_data.name,
                "account_number": beneficiary_data.account_number
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add beneficiary for user {user_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": "Failed to add beneficiary"}
    
    async def list_beneficiaries(self, user_id: str) -> Dict[str, Any]:
        """
        List all beneficiaries for a user.
        Returns simplified response without wrapper structure.
        """
        try:
            # Read beneficiaries
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return {"beneficiaries": []}
            
            # Filter by user
            user_beneficiaries = beneficiaries_df[
                beneficiaries_df['owner_user_id'] == user_id
            ].copy()
            
            if user_beneficiaries.empty:
                return {"beneficiaries": []}
            
            # Sort by added date (newest first)
            user_beneficiaries = user_beneficiaries.sort_values('added_at', ascending=False)
            
            # Convert to simplified list format (no added_at)
            beneficiaries_list = []
            for _, row in user_beneficiaries.iterrows():
                beneficiary_item = {
                    'beneficiary_id': row['beneficiary_id'],
                    'name': row['name'],
                    'account_number': row['account_number']
                }
                beneficiaries_list.append(beneficiary_item)
            
            self.logger.info(f"Beneficiaries list retrieved for user {user_id}: {len(beneficiaries_list)} beneficiaries")
            
            return {"beneficiaries": beneficiaries_list}
            
        except Exception as e:
            self.logger.error(f"Failed to list beneficiaries for user {user_id}: {str(e)}")
            return {"error": "Failed to retrieve beneficiaries"}
    
    async def search_beneficiaries(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Search beneficiaries by name for a user.
        Returns simplified response without wrapper structure.
        """
        try:
            # Read beneficiaries
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return {
                    "query": query,
                    "matches": [],
                    "total_matches": 0
                }
            
            # Filter by user
            user_beneficiaries = beneficiaries_df[
                beneficiaries_df['owner_user_id'] == user_id
            ]
            
            # Search by name (case-insensitive)
            matches = user_beneficiaries[
                user_beneficiaries['name'].str.contains(query, case=False, na=False)
            ]
            
            # Convert matches to simplified list (no added_at)
            match_list = []
            for _, row in matches.iterrows():
                match_item = {
                    'beneficiary_id': row['beneficiary_id'],
                    'name': row['name'],
                    'account_number': row['account_number']
                }
                match_list.append(match_item)
            
            self.logger.info(f"Search completed for user {user_id}, query '{query}': {len(match_list)} matches")
            
            return {
                "query": query,
                "matches": match_list,
                "total_matches": len(match_list)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search beneficiaries for user {user_id}: {str(e)}")
            return {"error": "Search failed"}
    
    async def remove_beneficiary(self, user_id: str, beneficiary_id: str) -> Dict[str, Any]:
        """
        Remove a beneficiary for the user.
        Returns simplified response without wrapper structure.
        """
        try:
            # Read beneficiaries
            beneficiaries_df = await self.storage.read_csv(self.settings.beneficiaries_csv)
            
            if beneficiaries_df.empty:
                return {"error": "Beneficiary not found"}
            
            # Find the beneficiary
            beneficiary_to_remove = beneficiaries_df[
                (beneficiaries_df['owner_user_id'] == user_id) &
                (beneficiaries_df['beneficiary_id'] == beneficiary_id)
            ]
            
            if beneficiary_to_remove.empty:
                return {"error": "Beneficiary not found"}
            
            # Get beneficiary details before removal
            beneficiary_name = beneficiary_to_remove.iloc[0]['name']
            
            # Remove beneficiary from dataframe
            beneficiaries_df = beneficiaries_df[
                ~((beneficiaries_df['owner_user_id'] == user_id) &
                  (beneficiaries_df['beneficiary_id'] == beneficiary_id))
            ]
            
            # Save updated CSV
            import os
            csv_path = os.path.join('data', 'beneficiaries.csv')
            beneficiaries_df.to_csv(csv_path, index=False)
            
            self.logger.info(f"Beneficiary removed for user {user_id}: {beneficiary_name}")
            
            # Return simplified response (no removed_at)
            return {
                "beneficiary_id": beneficiary_id,
                "name": beneficiary_name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to remove beneficiary {beneficiary_id} for user {user_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": "Failed to remove beneficiary"}


# Service instance management
_beneficiary_service_instance = None

def get_beneficiary_service() -> BeneficiaryService:
    """Get or create beneficiary service instance."""
    global _beneficiary_service_instance
    if _beneficiary_service_instance is None:
        _beneficiary_service_instance = BeneficiaryService()
    return _beneficiary_service_instance
