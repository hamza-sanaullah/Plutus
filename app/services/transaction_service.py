"""
Plutus Backend - Transaction Management Service
Handles money transfer operations between user accounts and beneficiaries.

Team: Yay!
Date: August 29, 2025
"""

from typing import Dict, Any, Optional, List
import pandas as pd
from decimal import Decimal

from .base_service import BaseService
from ..schemas.transaction_schemas import (
    TransactionRequest,
    TransactionHistoryRequest,
    TransactionStatusRequest
)


class TransactionService(BaseService):
    """
    Transaction service for all money transfer operations.
    """
    
    async def send_money(
        self,
        user_id: str,
        transaction_data: TransactionRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send money to a beneficiary.
        """
        try:
            # Validate user exists
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            # Validate beneficiary exists for this user
            beneficiary = await self.get_beneficiary_by_id_for_transaction(
                user_id, 
                transaction_data.beneficiary_id
            )
            if not beneficiary:
                return self.create_error_response(
                    "Beneficiary not found",
                    "BENEFICIARY_NOT_FOUND"
                )
            
            # Validate amount
            amount = transaction_data.amount
            if amount <= 0:
                return self.create_error_response(
                    "Amount must be greater than zero",
                    "INVALID_AMOUNT"
                )
            
            # Check minimum transfer amount
            if amount < self.settings.min_transfer_amount:
                return self.create_error_response(
                    f"Minimum transfer amount is PKR {self.settings.min_transfer_amount}",
                    "AMOUNT_TOO_LOW"
                )
            
            # Check maximum transfer amount
            if amount > self.settings.max_transfer_amount:
                return self.create_error_response(
                    f"Maximum transfer amount is PKR {self.settings.max_transfer_amount}",
                    "AMOUNT_TOO_HIGH"
                )
            
            # Check user balance
            user_balance = Decimal(user.get('balance', 0))
            if user_balance < amount:
                return self.create_error_response(
                    f"Insufficient balance. Available: PKR {user_balance}",
                    "INSUFFICIENT_BALANCE"
                )
            
            # Check daily transfer limit
            daily_check = await self.check_daily_transfer_limit(user_id, amount)
            if not daily_check["allowed"]:
                return self.create_error_response(
                    daily_check["message"],
                    "DAILY_LIMIT_EXCEEDED"
                )
            
            # Generate transaction ID
            transaction_id = self.security.generate_transaction_id()
            
            # Create transaction record
            transaction_record = {
                "transaction_id": transaction_id,
                "sender_user_id": user_id,
                "sender_name": user['full_name'],
                "sender_account": user['account_number'],
                "beneficiary_id": transaction_data.beneficiary_id,
                "beneficiary_name": beneficiary['name'],
                "beneficiary_account": beneficiary['account_number'],
                "beneficiary_bank": beneficiary['bank_name'],
                "amount": float(amount),
                "transaction_fee": 0.0,  # No fee for now
                "total_amount": float(amount),
                "description": transaction_data.description or "Money transfer",
                "status": "processing",
                "created_at": self.create_timestamp(),
                "completed_at": None,
                "failure_reason": None
            }
            
            # Process the transaction in steps
            
            # Step 1: Deduct amount from sender
            balance_update = await self.update_user_balance(
                user_id, 
                -amount, 
                f"Transfer to {beneficiary['name']}"
            )
            
            if not balance_update["success"]:
                return self.create_error_response(
                    "Failed to deduct amount from your account",
                    "BALANCE_UPDATE_FAILED"
                )
            
            # Step 2: Update daily transfer limit
            limit_update = await self.update_daily_transfer_limit(user_id, amount)
            if not limit_update:
                # Rollback balance update
                await self.update_user_balance(
                    user_id, 
                    amount, 
                    f"Rollback failed transfer to {beneficiary['name']}"
                )
                return self.create_error_response(
                    "Failed to update daily limits",
                    "LIMIT_UPDATE_FAILED"
                )
            
            # Step 3: Complete transaction
            transaction_record["status"] = "completed"
            transaction_record["completed_at"] = self.create_timestamp()
            
            # Save transaction to CSV
            success = await self.storage.append_csv(
                self.settings.transactions_csv,
                transaction_record
            )
            
            if not success:
                # Rollback all changes
                await self.update_user_balance(
                    user_id, 
                    amount, 
                    f"Rollback failed transfer to {beneficiary['name']}"
                )
                await self.rollback_daily_transfer_limit(user_id, amount)
                
                return self.create_error_response(
                    "Failed to record transaction",
                    "TRANSACTION_RECORD_FAILED"
                )
            
            # Get updated user balance
            updated_user = await self.get_user_by_id(user_id)
            new_balance = Decimal(updated_user.get('balance', 0))
            
            # Log transaction
            await self.log_audit(
                user_id=user_id,
                action="money_transfer",
                details={
                    "transaction_id": transaction_id,
                    "beneficiary_name": beneficiary['name'],
                    "amount": float(amount),
                    "new_balance": float(new_balance)
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(
                f"Money transfer completed: {user_id} -> {beneficiary['name']} "
                f"PKR {amount} (Transaction: {transaction_id})"
            )
            
            return self.create_success_response(
                "Money transfer completed successfully",
                {
                    "transaction_id": transaction_id,
                    "amount": float(amount),
                    "beneficiary_name": beneficiary['name'],
                    "new_balance": float(new_balance),
                    "transaction_time": transaction_record["completed_at"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process money transfer for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Transaction failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def get_transaction_history(
        self,
        user_id: str,
        history_request: TransactionHistoryRequest
    ) -> Dict[str, Any]:
        """
        Get transaction history for a user with filtering and pagination.
        """
        try:
            transactions_df = await self.storage.read_csv(self.settings.transactions_csv)
            
            if transactions_df.empty:
                return self.create_success_response(
                    "Transaction history retrieved successfully",
                    {
                        "data": [],
                        "pagination": {
                            "current_page": 1,
                            "page_size": history_request.page_size,
                            "total_items": 0,
                            "total_pages": 0,
                            "has_next": False,
                            "has_previous": False
                        },
                        "summary": {
                            "total_sent": 0.0,
                            "total_transactions": 0
                        }
                    }
                )
            
            # Filter by user
            user_transactions = transactions_df[
                transactions_df['sender_user_id'] == user_id
            ].copy()
            
            # Apply status filter
            if history_request.status_filter:
                user_transactions = user_transactions[
                    user_transactions['status'] == history_request.status_filter
                ]
            
            # Apply date range filter
            if history_request.start_date:
                user_transactions = user_transactions[
                    pd.to_datetime(user_transactions['created_at']) >= 
                    pd.to_datetime(history_request.start_date)
                ]
            
            if history_request.end_date:
                user_transactions = user_transactions[
                    pd.to_datetime(user_transactions['created_at']) <= 
                    pd.to_datetime(history_request.end_date)
                ]
            
            # Apply beneficiary filter
            if history_request.beneficiary_name:
                user_transactions = user_transactions[
                    user_transactions['beneficiary_name'].str.contains(
                        history_request.beneficiary_name, case=False, na=False
                    )
                ]
            
            # Sort by date (newest first)
            user_transactions = user_transactions.sort_values('created_at', ascending=False)
            
            # Calculate summary
            completed_transactions = user_transactions[
                user_transactions['status'] == 'completed'
            ]
            total_sent = completed_transactions['amount'].sum() if not completed_transactions.empty else 0.0
            total_transactions = len(user_transactions)
            
            # Pagination
            total_items = len(user_transactions)
            start_idx = (history_request.page - 1) * history_request.page_size
            end_idx = start_idx + history_request.page_size
            
            paginated_transactions = user_transactions.iloc[start_idx:end_idx]
            
            # Format transactions
            transactions = []
            for _, row in paginated_transactions.iterrows():
                transactions.append({
                    "transaction_id": row['transaction_id'],
                    "beneficiary_name": row['beneficiary_name'],
                    "beneficiary_bank": row['beneficiary_bank'],
                    "amount": row['amount'],
                    "description": row['description'],
                    "status": row['status'],
                    "created_at": row['created_at'],
                    "completed_at": row['completed_at'],
                    "failure_reason": row.get('failure_reason')
                })
            
            # Pagination info
            total_pages = (total_items + history_request.page_size - 1) // history_request.page_size
            
            pagination = {
                "current_page": history_request.page,
                "page_size": history_request.page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": history_request.page < total_pages,
                "has_previous": history_request.page > 1
            }
            
            return self.create_success_response(
                "Transaction history retrieved successfully",
                {
                    "data": transactions,
                    "pagination": pagination,
                    "summary": {
                        "total_sent": total_sent,
                        "total_transactions": total_transactions
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction history for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve transaction history",
                "INTERNAL_ERROR"
            )
    
    async def get_transaction_status(
        self,
        user_id: str,
        status_request: TransactionStatusRequest
    ) -> Dict[str, Any]:
        """
        Get status of a specific transaction.
        """
        try:
            transactions_df = await self.storage.read_csv(self.settings.transactions_csv)
            
            if transactions_df.empty:
                return self.create_error_response(
                    "Transaction not found",
                    "TRANSACTION_NOT_FOUND"
                )
            
            # Find transaction
            transaction = transactions_df[
                (transactions_df['transaction_id'] == status_request.transaction_id) &
                (transactions_df['sender_user_id'] == user_id)
            ]
            
            if transaction.empty:
                return self.create_error_response(
                    "Transaction not found",
                    "TRANSACTION_NOT_FOUND"
                )
            
            transaction_data = transaction.iloc[0]
            
            return self.create_success_response(
                "Transaction status retrieved successfully",
                {
                    "transaction_id": transaction_data['transaction_id'],
                    "beneficiary_name": transaction_data['beneficiary_name'],
                    "beneficiary_bank": transaction_data['beneficiary_bank'],
                    "amount": transaction_data['amount'],
                    "description": transaction_data['description'],
                    "status": transaction_data['status'],
                    "created_at": transaction_data['created_at'],
                    "completed_at": transaction_data['completed_at'],
                    "failure_reason": transaction_data.get('failure_reason')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction status for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve transaction status",
                "INTERNAL_ERROR"
            )
    
    async def check_daily_transfer_limit(
        self,
        user_id: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Check if user can transfer the amount without exceeding daily limit.
        """
        try:
            # Get user's current daily transfer info
            daily_info = await self.get_user_daily_transfer_info(user_id)
            
            current_date = self.create_date()
            
            # Reset if new day
            if daily_info["date"] != current_date:
                daily_info = {
                    "date": current_date,
                    "transferred_amount": Decimal(0),
                    "transaction_count": 0
                }
            
            # Calculate new amounts
            new_amount = daily_info["transferred_amount"] + amount
            new_count = daily_info["transaction_count"] + 1
            
            # Check limits
            if new_amount > self.settings.daily_transfer_limit:
                remaining = self.settings.daily_transfer_limit - daily_info["transferred_amount"]
                return {
                    "allowed": False,
                    "message": f"Daily transfer limit exceeded. Remaining: PKR {remaining}",
                    "remaining_amount": float(remaining),
                    "remaining_transactions": max(0, self.settings.daily_transaction_limit - daily_info["transaction_count"])
                }
            
            if new_count > self.settings.daily_transaction_limit:
                remaining_transactions = self.settings.daily_transaction_limit - daily_info["transaction_count"]
                return {
                    "allowed": False,
                    "message": f"Daily transaction limit exceeded. Remaining: {remaining_transactions}",
                    "remaining_amount": float(self.settings.daily_transfer_limit - daily_info["transferred_amount"]),
                    "remaining_transactions": remaining_transactions
                }
            
            return {
                "allowed": True,
                "message": "Transfer allowed",
                "remaining_amount": float(self.settings.daily_transfer_limit - new_amount),
                "remaining_transactions": self.settings.daily_transaction_limit - new_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check daily transfer limit for user {user_id}: {str(e)}")
            return {
                "allowed": False,
                "message": "Unable to verify daily limits",
                "remaining_amount": 0.0,
                "remaining_transactions": 0
            }
    
    async def get_beneficiary_by_id_for_transaction(
        self,
        user_id: str,
        beneficiary_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get beneficiary details for transaction processing.
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
            self.logger.error(f"Failed to get beneficiary {beneficiary_id} for transaction: {str(e)}")
            return None
    
    async def update_daily_transfer_limit(self, user_id: str, amount: Decimal) -> bool:
        """
        Update user's daily transfer limit tracking.
        """
        try:
            # Get current daily info
            daily_info = await self.get_user_daily_transfer_info(user_id)
            
            current_date = self.create_date()
            
            # Reset if new day
            if daily_info["date"] != current_date:
                daily_info = {
                    "date": current_date,
                    "transferred_amount": Decimal(0),
                    "transaction_count": 0
                }
            
            # Update amounts
            new_amount = daily_info["transferred_amount"] + amount
            new_count = daily_info["transaction_count"] + 1
            
            # Update user daily limits
            success = await self.storage.update_row(
                self.settings.users_csv,
                {"user_id": user_id},
                {
                    "daily_transfer_date": current_date,
                    "daily_transferred_amount": float(new_amount),
                    "daily_transaction_count": new_count
                }
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update daily transfer limit for user {user_id}: {str(e)}")
            return False
    
    async def rollback_daily_transfer_limit(self, user_id: str, amount: Decimal) -> bool:
        """
        Rollback daily transfer limit update.
        """
        try:
            # Get current daily info
            daily_info = await self.get_user_daily_transfer_info(user_id)
            
            # Rollback amounts
            new_amount = max(Decimal(0), daily_info["transferred_amount"] - amount)
            new_count = max(0, daily_info["transaction_count"] - 1)
            
            # Update user daily limits
            success = await self.storage.update_row(
                self.settings.users_csv,
                {"user_id": user_id},
                {
                    "daily_transferred_amount": float(new_amount),
                    "daily_transaction_count": new_count
                }
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to rollback daily transfer limit for user {user_id}: {str(e)}")
            return False


# Global instance
transaction_service = TransactionService()


def get_transaction_service() -> TransactionService:
    """
    Dependency to get transaction service instance.
    """
    return transaction_service
