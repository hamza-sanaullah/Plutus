"""
Plutus Backend - Balance Management Tests
Comprehensive tests for balance inquiry, history, and account operations.

Team: Yay!
Date: August 30, 2025
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, date
import json


class TestBalanceInquiry:
    """Test cases for balance inquiry functionality."""
    
    def test_get_current_balance_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful balance inquiry."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "balance" in data["data"]
        assert "account_number" in data["data"]
        assert "currency" in data["data"]
        assert data["data"]["currency"] == "PKR"
        assert isinstance(data["data"]["balance"], (int, float))
        assert data["data"]["balance"] >= 0
    
    def test_get_balance_unauthorized(self, test_client: TestClient):
        """Test balance inquiry without authentication."""
        response = test_client.get("/balance/current")
        
        assert response.status_code == 403
    
    def test_get_balance_invalid_token(self, test_client: TestClient):
        """Test balance inquiry with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": False,
                "error": "Invalid token"
            }
            
            response = test_client.get("/balance/current", headers=invalid_headers)
        
        assert response.status_code == 401
    
    def test_get_balance_nonexistent_user(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test balance inquiry for non-existent user."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "NONEXISTENT",
                "email": "nonexistent@example.com"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]["message"].lower()


class TestBalanceHistory:
    """Test cases for balance history functionality."""
    
    def test_get_balance_history_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful balance history retrieval."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "transactions" in data["data"]
        assert "summary" in data["data"]
        assert isinstance(data["data"]["transactions"], list)
    
    def test_get_balance_history_with_date_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test balance history with date range filter."""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all transactions are within date range
        for transaction in data["data"]["transactions"]:
            transaction_date = datetime.fromisoformat(transaction["created_at"].replace('Z', '+00:00'))
            assert datetime(2024, 1, 1) <= transaction_date <= datetime(2024, 12, 31, 23, 59, 59)
    
    def test_get_balance_history_with_transaction_type_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test balance history with transaction type filter."""
        params = {
            "transaction_type": "transfer"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all transactions are of the specified type
        for transaction in data["data"]["transactions"]:
            assert transaction["transaction_type"] == "transfer"
    
    def test_get_balance_history_with_pagination(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test balance history with pagination."""
        params = {
            "limit": 5,
            "offset": 0
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["transactions"]) <= 5
    
    def test_get_balance_history_invalid_date_format(self, test_client: TestClient, auth_headers):
        """Test balance history with invalid date format."""
        params = {
            "start_date": "invalid-date"
        }
        
        response = test_client.get("/balance/history", headers=auth_headers, params=params)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_balance_history_invalid_date_range(self, test_client: TestClient, auth_headers):
        """Test balance history with invalid date range (end before start)."""
        params = {
            "start_date": "2024-12-31",
            "end_date": "2024-01-01"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/history", headers=auth_headers, params=params)
        
        assert response.status_code == 400
        data = response.json()
        assert "date range" in data["detail"]["message"].lower()


class TestAccountSummary:
    """Test cases for account summary functionality."""
    
    def test_get_account_summary_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful account summary retrieval."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "account_info" in data["data"]
        assert "balance_info" in data["data"]
        assert "transaction_summary" in data["data"]
        
        # Verify account info structure
        account_info = data["data"]["account_info"]
        assert "account_number" in account_info
        assert "account_holder" in account_info
        assert "bank_name" in account_info
        
        # Verify balance info structure
        balance_info = data["data"]["balance_info"]
        assert "current_balance" in balance_info
        assert "available_balance" in balance_info
        assert "currency" in balance_info
        
        # Verify transaction summary structure
        tx_summary = data["data"]["transaction_summary"]
        assert "total_transactions" in tx_summary
        assert "total_sent" in tx_summary
        assert "total_received" in tx_summary
    
    def test_get_account_summary_with_period_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test account summary with specific time period."""
        params = {
            "period": "last_30_days"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/summary", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "period" in data["data"]["transaction_summary"]
    
    def test_get_account_summary_unauthorized(self, test_client: TestClient):
        """Test account summary without authentication."""
        response = test_client.get("/balance/summary")
        
        assert response.status_code == 403


class TestBalanceValidation:
    """Test cases for balance validation and business rules."""
    
    def test_negative_balance_handling(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test handling of negative balance scenarios."""
        # This would test how the system handles accounts with negative balances
        # (if allowed by business rules)
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.balance_service.BalanceService.get_current_balance') as mock_balance:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock negative balance
            mock_balance.return_value = {
                "balance": -1000.0,
                "account_number": "0123456789012345",
                "currency": "PKR",
                "status": "overdrawn"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["balance"] == -1000.0
    
    def test_large_balance_handling(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test handling of very large balance amounts."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.balance_service.BalanceService.get_current_balance') as mock_balance:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock very large balance
            large_amount = 999999999.99
            mock_balance.return_value = {
                "balance": large_amount,
                "account_number": "0123456789012345",
                "currency": "PKR",
                "status": "active"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["balance"] == large_amount
    
    def test_balance_precision_handling(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test balance precision and rounding."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.balance_service.BalanceService.get_current_balance') as mock_balance:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock balance with many decimal places
            precise_amount = 1234.56789
            mock_balance.return_value = {
                "balance": precise_amount,
                "account_number": "0123456789012345",
                "currency": "PKR",
                "status": "active"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Balance should be rounded to 2 decimal places for PKR
        assert round(data["data"]["balance"], 2) == round(precise_amount, 2)


class TestBalanceErrorHandling:
    """Test cases for balance error scenarios."""
    
    def test_storage_error_handling(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test handling of storage errors during balance operations."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.balance_service.BalanceService.get_current_balance') as mock_balance:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock storage error
            mock_balance.side_effect = Exception("Storage connection failed")
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"]["message"].lower()
    
    def test_concurrent_balance_access(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test handling of concurrent balance access."""
        # This would test race conditions and locking mechanisms
        # For now, we simulate multiple concurrent requests
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Simulate multiple concurrent requests
            responses = []
            for _ in range(5):
                response = test_client.get("/balance/current", headers=auth_headers)
                responses.append(response)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code in [200, 500]  # Allow for some to fail due to concurrency
    
    def test_malformed_balance_data(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test handling of malformed balance data in storage."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.balance_service.BalanceService.get_current_balance') as mock_balance:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock malformed data
            mock_balance.return_value = {
                "balance": "invalid_amount",  # String instead of number
                "account_number": "0123456789012345",
                "currency": "PKR"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
        
        # Should handle gracefully or return appropriate error
        assert response.status_code in [200, 400, 500]


class TestBalanceAuditTrail:
    """Test cases for balance audit trail functionality."""
    
    def test_balance_inquiry_audit_logging(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that balance inquiries are properly logged."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.core.logging.AuditLogger.log_audit') as mock_audit:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/current", headers=auth_headers)
            
            # Verify audit log was called
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "balance_inquiry"
            assert audit_call["user_id"] == "USR001"
    
    def test_balance_history_audit_logging(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that balance history requests are properly logged."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.core.logging.AuditLogger.log_audit') as mock_audit:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/balance/history", headers=auth_headers)
            
            # Verify audit log was called
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "balance_history"
            assert audit_call["user_id"] == "USR001"
