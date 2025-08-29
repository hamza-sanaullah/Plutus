"""
Plutus Backend - Balance Management Service
Handles balance operations, deposits, withdrawals, and balance history.

Team: Yay!
Date: August 29, 2025
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from .base_service import BaseService
from ..schemas.balance_schemas import (
    DepositRequest,
    WithdrawRequest,
    BalanceHistoryRequest,
    DailyLimitUpdateRequest
)


class BalanceService(BaseService):
    """
    Balance management service for all balance-related operations.
    """
    
    async def check_balance(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current balance and related information for a user.
        """
        try:
            # Get user data
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            # Calculate daily spent amount
            daily_limit_check = await self.check_daily_limit(user_id, 0)
            
            # Get last transaction timestamp
            transactions_df = await self.storage.read_csv(self.settings.transactions_csv)
            last_transaction = None
            
            if not transactions_df.empty:
                user_transactions = transactions_df[
                    (transactions_df['from_user_id'] == user_id) |
                    (transactions_df['to_user_id'] == user_id)
                ].sort_values('timestamp', ascending=False)
                
                if not user_transactions.empty:
                    last_transaction = user_transactions.iloc[0]['timestamp']
            
            # Log balance check
            await self.log_audit(
                user_id=user_id,
                action="balance_check",
                details={
                    "current_balance": float(user['balance']),
                    "daily_spent": daily_limit_check.get('daily_spent', 0)
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            return self.create_success_response(
                "Balance retrieved successfully",
                {
                    "user_id": user['user_id'],
                    "account_number": user['account_number'],
                    "current_balance": float(user['balance']),
                    "daily_limit": float(user['daily_limit']),
                    "daily_spent_today": daily_limit_check.get('daily_spent', 0),
                    "available_daily_limit": daily_limit_check.get('remaining_limit', 0) + daily_limit_check.get('daily_spent', 0),
                    "currency": self.settings.default_currency,
                    "last_transaction": last_transaction
                }
            )
            
        except Exception as e:
            self.logger.error(f"Balance check failed for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve balance",
                "INTERNAL_ERROR"
            )
    
    async def deposit_money(
        self,
        user_id: str,
        deposit_data: DepositRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deposit money to user account.
        """
        try:
            # Get current user data
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            current_balance = float(user['balance'])
            new_balance = current_balance + deposit_data.amount
            
            # Generate transaction ID
            transaction_id = self.security.generate_transaction_id()
            
            # Update user balance
            success = await self.update_user_balance(
                user_id=user_id,
                new_balance=new_balance,
                operation="deposit",
                amount=deposit_data.amount,
                description=deposit_data.description
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to update balance",
                    "UPDATE_FAILED"
                )
            
            # Record transaction
            transaction_data = {
                "transaction_id": transaction_id,
                "from_user_id": "SYSTEM",  # System deposit
                "to_user_id": user_id,
                "from_account": "SYSTEM",
                "to_account": user['account_number'],
                "amount": deposit_data.amount,
                "status": "success",
                "description": deposit_data.description or "Balance deposit",
                "timestamp": self.create_timestamp(),
                "daily_total_sent": 0.0  # Not applicable for deposits
            }
            
            await self.storage.append_csv(self.settings.transactions_csv, transaction_data)
            
            # Log deposit operation
            await self.log_audit(
                user_id=user_id,
                action="deposit",
                details={
                    "transaction_id": transaction_id,
                    "amount": deposit_data.amount,
                    "previous_balance": current_balance,
                    "new_balance": new_balance,
                    "description": deposit_data.description
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Deposit successful for user {user_id}: {deposit_data.amount}")
            
            return self.create_success_response(
                "Deposit completed successfully",
                {
                    "transaction_id": transaction_id,
                    "user_id": user_id,
                    "amount_deposited": deposit_data.amount,
                    "previous_balance": current_balance,
                    "new_balance": new_balance,
                    "currency": deposit_data.currency,
                    "description": deposit_data.description,
                    "timestamp": transaction_data["timestamp"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Deposit failed for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Deposit failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def withdraw_money(
        self,
        user_id: str,
        withdraw_data: WithdrawRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Withdraw money from user account.
        """
        try:
            # Get current user data
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            current_balance = float(user['balance'])
            
            # Check sufficient balance
            if current_balance < withdraw_data.amount:
                await self.log_audit(
                    user_id=user_id,
                    action="withdrawal_failed",
                    details={
                        "amount": withdraw_data.amount,
                        "current_balance": current_balance,
                        "reason": "Insufficient funds"
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                
                return self.create_error_response(
                    "Insufficient funds",
                    "INSUFFICIENT_FUNDS"
                )
            
            new_balance = current_balance - withdraw_data.amount
            
            # Generate transaction ID
            transaction_id = self.security.generate_transaction_id()
            
            # Update user balance
            success = await self.update_user_balance(
                user_id=user_id,
                new_balance=new_balance,
                operation="withdraw",
                amount=withdraw_data.amount,
                description=withdraw_data.description
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to update balance",
                    "UPDATE_FAILED"
                )
            
            # Record transaction
            transaction_data = {
                "transaction_id": transaction_id,
                "from_user_id": user_id,
                "to_user_id": "SYSTEM",  # System withdrawal
                "from_account": user['account_number'],
                "to_account": "SYSTEM",
                "amount": withdraw_data.amount,
                "status": "success",
                "description": withdraw_data.description or "Balance withdrawal",
                "timestamp": self.create_timestamp(),
                "daily_total_sent": 0.0  # Not counted in daily limit
            }
            
            await self.storage.append_csv(self.settings.transactions_csv, transaction_data)
            
            # Log withdrawal operation
            await self.log_audit(
                user_id=user_id,
                action="withdrawal",
                details={
                    "transaction_id": transaction_id,
                    "amount": withdraw_data.amount,
                    "previous_balance": current_balance,
                    "new_balance": new_balance,
                    "description": withdraw_data.description
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Withdrawal successful for user {user_id}: {withdraw_data.amount}")
            
            return self.create_success_response(
                "Withdrawal completed successfully",
                {
                    "transaction_id": transaction_id,
                    "user_id": user_id,
                    "amount_withdrawn": withdraw_data.amount,
                    "previous_balance": current_balance,
                    "new_balance": new_balance,
                    "currency": withdraw_data.currency,
                    "description": withdraw_data.description,
                    "timestamp": transaction_data["timestamp"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Withdrawal failed for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Withdrawal failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def get_balance_history(
        self,
        user_id: str,
        history_request: BalanceHistoryRequest
    ) -> Dict[str, Any]:
        """
        Get balance history with filtering and pagination.
        """
        try:
            # Get all transactions for the user
            transactions_df = await self.storage.read_csv(self.settings.transactions_csv)
            
            if transactions_df.empty:
                return self.create_success_response(
                    "Balance history retrieved",
                    {
                        "transactions": [],
                        "pagination": {
                            "current_page": 1,
                            "page_size": history_request.page_size,
                            "total_items": 0,
                            "total_pages": 0,
                            "has_next": False,
                            "has_previous": False
                        },
                        "summary": {
                            "total_deposits": 0.0,
                            "total_withdrawals": 0.0,
                            "net_change": 0.0,
                            "transaction_count": 0
                        }
                    }
                )
            
            # Filter transactions for this user (deposits and withdrawals)
            user_transactions = transactions_df[
                ((transactions_df['to_user_id'] == user_id) & (transactions_df['from_user_id'] == 'SYSTEM')) |
                ((transactions_df['from_user_id'] == user_id) & (transactions_df['to_user_id'] == 'SYSTEM'))
            ].copy()
            
            # Apply date filters
            if history_request.start_date:
                user_transactions = user_transactions[
                    user_transactions['timestamp'] >= history_request.start_date.isoformat()
                ]
            
            if history_request.end_date:
                user_transactions = user_transactions[
                    user_transactions['timestamp'] <= history_request.end_date.isoformat()
                ]
            
            # Apply transaction type filter
            if history_request.transaction_type and history_request.transaction_type != 'all':
                if history_request.transaction_type == 'deposit':
                    user_transactions = user_transactions[
                        user_transactions['from_user_id'] == 'SYSTEM'
                    ]
                elif history_request.transaction_type == 'withdraw':
                    user_transactions = user_transactions[
                        user_transactions['to_user_id'] == 'SYSTEM'
                    ]
            
            # Sort by timestamp (newest first)
            user_transactions = user_transactions.sort_values('timestamp', ascending=False)
            
            # Calculate summary
            deposits = user_transactions[user_transactions['from_user_id'] == 'SYSTEM']['amount'].sum()
            withdrawals = user_transactions[user_transactions['to_user_id'] == 'SYSTEM']['amount'].sum()
            
            summary = {
                "total_deposits": float(deposits) if pd.notna(deposits) else 0.0,
                "total_withdrawals": float(withdrawals) if pd.notna(withdrawals) else 0.0,
                "net_change": float(deposits - withdrawals) if pd.notna(deposits) and pd.notna(withdrawals) else 0.0,
                "transaction_count": len(user_transactions)
            }
            
            # Pagination
            total_items = len(user_transactions)
            start_idx = (history_request.page - 1) * history_request.page_size
            end_idx = start_idx + history_request.page_size
            
            paginated_transactions = user_transactions.iloc[start_idx:end_idx]
            
            # Format transactions
            transactions = []
            for _, row in paginated_transactions.iterrows():
                transaction_type = "deposit" if row['from_user_id'] == 'SYSTEM' else "withdraw"
                
                transactions.append({
                    "transaction_id": row['transaction_id'],
                    "type": transaction_type,
                    "amount": float(row['amount']),
                    "description": row['description'],
                    "timestamp": row['timestamp']
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
                "Balance history retrieved",
                {
                    "transactions": transactions,
                    "pagination": pagination,
                    "summary": summary
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get balance history for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve balance history",
                "INTERNAL_ERROR"
            )
    
    async def update_daily_limit(
        self,
        user_id: str,
        limit_request: DailyLimitUpdateRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user's daily transaction limit.
        """
        try:
            # Get current user data
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            previous_limit = float(user['daily_limit'])
            
            # Update daily limit
            success = await self.storage.update_row(
                self.settings.users_csv,
                {"user_id": user_id},
                {"daily_limit": limit_request.new_daily_limit}
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to update daily limit",
                    "UPDATE_FAILED"
                )
            
            # Log limit update
            await self.log_audit(
                user_id=user_id,
                action="daily_limit_updated",
                details={
                    "previous_limit": previous_limit,
                    "new_limit": limit_request.new_daily_limit
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Daily limit updated for user {user_id}: {previous_limit} -> {limit_request.new_daily_limit}")
            
            return self.create_success_response(
                "Daily limit updated successfully",
                {
                    "user_id": user_id,
                    "previous_daily_limit": previous_limit,
                    "new_daily_limit": limit_request.new_daily_limit,
                    "effective_date": self.create_timestamp()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update daily limit for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to update daily limit",
                "INTERNAL_ERROR"
            )


# Global instance
balance_service = BalanceService()


def get_balance_service() -> BalanceService:
    """
    Dependency to get balance service instance.
    """
    return balance_service
