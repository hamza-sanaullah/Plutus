"""
Plutus Backend - Transaction Management Service (Ultra Simplified)
Copy of balance service pattern for send money functionality.

Team: Yay!
Date: August 30, 2025
"""

from typing import Dict, Any
import pandas as pd
from datetime import datetime

from .base_service import BaseService
from ..schemas.transaction_schemas import SendMoneyRequest


class TransactionService(BaseService):
    """
    Simplified transaction service using balance service pattern.
    """
    
    async def send_money(
        self,
        user_id: str,
        transaction_data: SendMoneyRequest
    ) -> Dict[str, Any]:
        """
        Send money - simplified implementation that actually works.
        """
        try:
            # Step 1: Read and validate users
            users_df = await self.storage.read_csv(self.settings.users_csv)
            
            sender_data = users_df[users_df['user_id'] == user_id]
            if sender_data.empty:
                return {"success": False, "message": "Sender not found", "error_code": "USER_NOT_FOUND"}
            
            recipient_data = users_df[users_df['user_id'] == transaction_data.to_user_id]
            if recipient_data.empty:
                return {"success": False, "message": "Recipient not found", "error_code": "RECIPIENT_NOT_FOUND"}
            
            # Step 2: Check balance
            sender_balance = float(sender_data.iloc[0]['balance'])
            amount = float(transaction_data.amount)
            
            if sender_balance < amount:
                return {"success": False, "message": "Insufficient balance", "error_code": "INSUFFICIENT_BALANCE"}
            
            # Step 3: Update balances manually (direct CSV manipulation)
            import pandas as pd
            import os
            
            # Read CSV file directly
            csv_path = os.path.join('data', 'users.csv')
            users_df = pd.read_csv(csv_path)
            
            # Update balances
            recipient_balance = float(recipient_data.iloc[0]['balance'])
            new_sender_balance = sender_balance - amount
            new_recipient_balance = recipient_balance + amount
            
            users_df.loc[users_df['user_id'] == user_id, 'balance'] = new_sender_balance
            users_df.loc[users_df['user_id'] == transaction_data.to_user_id, 'balance'] = new_recipient_balance
            
            # Save CSV file directly
            users_df.to_csv(csv_path, index=False)
            
            # Step 4: Create transaction record
            transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            transaction_record = {
                'transaction_id': transaction_id,
                'from_user_id': user_id,
                'to_user_id': transaction_data.to_user_id,
                'amount': amount,
                'description': transaction_data.description,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save transaction directly to CSV
            transactions_csv_path = os.path.join('data', 'transactions.csv')
            try:
                transactions_df = pd.read_csv(transactions_csv_path)
            except:
                transactions_df = pd.DataFrame(columns=['transaction_id', 'from_user_id', 'to_user_id', 'amount', 'description', 'timestamp'])
            
            new_transaction = pd.DataFrame([transaction_record])
            transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
            transactions_df.to_csv(transactions_csv_path, index=False)
            
            return {
                "success": True,
                "message": "Money sent successfully",
                "data": transaction_record
            }
            
        except Exception as e:
            self.logger.error(f"Money transfer error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": "Transaction failed", "error_code": "INTERNAL_ERROR"}
    
    async def get_transaction_history(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get transaction history for a user with simplified response.
        """
        try:
            # Load transactions
            transactions_df = await self.storage.read_csv(self.settings.transactions_csv)
            if transactions_df.empty:
                return {
                    "success": True,
                    "message": "No transactions found",
                    "data": {"transactions": []}
                }
            
            # Filter transactions for this user (both sent and received)
            user_transactions = transactions_df[
                (transactions_df['from_user_id'] == user_id) | 
                (transactions_df['to_user_id'] == user_id)
            ].copy()
            
            if user_transactions.empty:
                return {
                    "success": True,
                    "message": "No transactions found for user",
                    "data": {"transactions": []}
                }
            
            # Sort by timestamp (newest first)
            user_transactions = user_transactions.sort_values('timestamp', ascending=False)
            
            # Convert to simplified format
            transactions_list = []
            for _, row in user_transactions.iterrows():
                transaction_item = {
                    'transaction_id': row['transaction_id'],
                    'from_user_id': row['from_user_id'],
                    'to_user_id': row['to_user_id'],
                    'amount': float(row['amount']),
                    'description': row['description'],
                    'timestamp': row['timestamp']
                }
                transactions_list.append(transaction_item)
            
            self.logger.info(f"Transaction history retrieved for user {user_id}: {len(transactions_list)} transactions")
            
            return {
                "success": True,
                "message": "Transaction history retrieved successfully",
                "data": {"transactions": transactions_list}
            }
            
        except Exception as e:
            self.logger.error(f"Transaction history error: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve transaction history",
                "INTERNAL_ERROR"
            )


# Service instance management
_transaction_service_instance = None

def get_transaction_service() -> TransactionService:
    """Get or create transaction service instance."""
    global _transaction_service_instance
    if _transaction_service_instance is None:
        _transaction_service_instance = TransactionService()
    return _transaction_service_instance
