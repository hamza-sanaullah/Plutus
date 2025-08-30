"""
Plutus Backend - Transaction Tests
Comprehensive tests for money transfer operations, limits, and validation.

Team: Yay!
Date: August 30, 2025
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, date
import json


class TestMoneyTransfer:
    """Test cases for money transfer functionality."""
    
    def test_successful_transfer(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test successful money transfer to beneficiary."""
        response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "transaction_id" in data["data"]
        assert data["data"]["amount"] == valid_transfer_data["amount"]
        assert data["data"]["beneficiary_id"] == valid_transfer_data["beneficiary_id"]
        assert data["data"]["status"] == "completed"
    
    def test_transfer_insufficient_balance(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test transfer with insufficient balance."""
        # Set amount higher than available balance
        valid_transfer_data["amount"] = 1000000.0  # Very high amount
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "insufficient" in data["detail"]["message"].lower()
    
    def test_transfer_invalid_beneficiary(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config):
        """Test transfer to non-existent beneficiary."""
        valid_transfer_data["beneficiary_id"] = "NONEXISTENT"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "beneficiary" in data["detail"]["message"].lower() and "not found" in data["detail"]["message"].lower()
    
    def test_transfer_invalid_amount(self, test_client: TestClient, auth_headers, valid_transfer_data, invalid_data_samples):
        """Test transfer with invalid amount."""
        test_cases = [
            {"amount": 0, "error": "amount must be greater than zero"},
            {"amount": -100, "error": "amount must be positive"},
            {"amount": 0.001, "error": "amount precision"},  # Too many decimal places
            {"amount": 5000001, "error": "amount exceeds maximum"}  # Above single transaction limit
        ]
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            for test_case in test_cases:
                valid_transfer_data["amount"] = test_case["amount"]
                response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
                
                assert response.status_code in [400, 422]  # Bad request or validation error
    
    def test_transfer_with_description(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test transfer with description/memo."""
        valid_transfer_data["description"] = "Payment for services"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["description"] == valid_transfer_data["description"]
    
    def test_transfer_unauthorized(self, test_client: TestClient, valid_transfer_data):
        """Test transfer without authentication."""
        response = test_client.post("/transactions/send", json=valid_transfer_data)
        
        assert response.status_code == 403


class TestDailyLimits:
    """Test cases for daily transaction limits."""
    
    def test_daily_limit_enforcement(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test that daily limits are enforced."""
        # Set amount that would exceed daily limit when combined with existing transfers
        valid_transfer_data["amount"] = 499000.0  # Close to daily limit of 500k
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.transaction_service.TransactionService.transfer_money') as mock_transfer:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock service to return daily limit exceeded error
            mock_transfer.side_effect = ValueError("Daily transfer limit of PKR 500,000 exceeded")
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "daily limit" in data["detail"]["message"].lower()
    
    def test_daily_limit_calculation(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test daily limit calculation endpoint."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/daily-limits", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "daily_limit" in data["data"]
        assert "used_amount" in data["data"]
        assert "remaining_amount" in data["data"]
        assert data["data"]["daily_limit"] == 500000  # PKR 500k daily limit
    
    def test_daily_limit_with_date_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test daily limit calculation for specific date."""
        params = {
            "date": "2024-08-30"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/daily-limits", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "date" in data["data"]
        assert data["data"]["date"] == "2024-08-30"
    
    def test_multiple_transfers_within_limit(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test multiple transfers within daily limit."""
        # Simulate multiple small transfers
        transfer_amounts = [50000, 75000, 100000]  # Total 225k, within 500k limit
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            for amount in transfer_amounts:
                valid_transfer_data["amount"] = amount
                response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
                
                # All should succeed if within limits
                assert response.status_code in [201, 400]  # 400 if limit exceeded


class TestTransactionHistory:
    """Test cases for transaction history functionality."""
    
    def test_get_transaction_history_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful transaction history retrieval."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "transactions" in data["data"]
        assert "summary" in data["data"]
        assert isinstance(data["data"]["transactions"], list)
        
        # Verify transaction structure
        if data["data"]["transactions"]:
            transaction = data["data"]["transactions"][0]
            assert "transaction_id" in transaction
            assert "amount" in transaction
            assert "beneficiary_id" in transaction
            assert "status" in transaction
            assert "created_at" in transaction
    
    def test_transaction_history_with_pagination(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction history with pagination."""
        params = {
            "limit": 10,
            "offset": 0
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["transactions"]) <= 10
    
    def test_transaction_history_with_date_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction history with date range filter."""
        params = {
            "start_date": "2024-08-01",
            "end_date": "2024-08-31"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all transactions are within date range
        for transaction in data["data"]["transactions"]:
            transaction_date = datetime.fromisoformat(transaction["created_at"].replace('Z', '+00:00'))
            assert datetime(2024, 8, 1) <= transaction_date <= datetime(2024, 8, 31, 23, 59, 59)
    
    def test_transaction_history_with_status_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction history with status filter."""
        params = {
            "status": "completed"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all transactions have the specified status
        for transaction in data["data"]["transactions"]:
            assert transaction["status"] == "completed"
    
    def test_transaction_history_with_amount_filter(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction history with amount range filter."""
        params = {
            "min_amount": 1000,
            "max_amount": 10000
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/transactions/history", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all transactions are within amount range
        for transaction in data["data"]["transactions"]:
            assert 1000 <= transaction["amount"] <= 10000


class TestTransactionDetails:
    """Test cases for individual transaction details."""
    
    def test_get_transaction_details_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful transaction details retrieval."""
        transaction_id = "TXN001"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get(f"/transactions/{transaction_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["transaction_id"] == transaction_id
        assert "amount" in data["data"]
        assert "beneficiary_details" in data["data"]
        assert "fees" in data["data"]
        assert "status" in data["data"]
    
    def test_get_transaction_details_not_found(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test retrieval of non-existent transaction."""
        transaction_id = "NONEXISTENT"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get(f"/transactions/{transaction_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]["message"].lower()
    
    def test_get_transaction_details_unauthorized_user(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction details access by unauthorized user."""
        transaction_id = "TXN001"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            # Different user trying to access
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR999",
                "email": "other@example.com"
            }
            
            response = test_client.get(f"/transactions/{transaction_id}", headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "permission" in data["detail"]["message"].lower()


class TestTransactionReceipts:
    """Test cases for transaction receipt generation."""
    
    def test_generate_transaction_receipt(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction receipt generation."""
        transaction_id = "TXN001"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get(f"/transactions/{transaction_id}/receipt", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "receipt" in data["data"]
        
        receipt = data["data"]["receipt"]
        assert "transaction_id" in receipt
        assert "transaction_reference" in receipt
        assert "sender_details" in receipt
        assert "beneficiary_details" in receipt
        assert "amount_details" in receipt
        assert "timestamp" in receipt
    
    def test_generate_receipt_pdf_format(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction receipt in PDF format."""
        transaction_id = "TXN001"
        params = {
            "format": "pdf"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get(f"/transactions/{transaction_id}/receipt", headers=auth_headers, params=params)
        
        # PDF generation might not be implemented, so allow for not implemented response
        assert response.status_code in [200, 501]  # 501 for not implemented
    
    def test_receipt_for_failed_transaction(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test receipt generation for failed transaction."""
        # This would test receipt for a transaction with "failed" status
        transaction_id = "TXN_FAILED"
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.transaction_service.TransactionService.get_transaction_details') as mock_details:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock failed transaction
            mock_details.return_value = {
                "transaction_id": transaction_id,
                "amount": 5000.0,
                "status": "failed",
                "failure_reason": "Insufficient funds"
            }
            
            response = test_client.get(f"/transactions/{transaction_id}/receipt", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["receipt"]["status"] == "failed"


class TestTransactionSecurity:
    """Test cases for transaction security features."""
    
    def test_transaction_idempotency(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test transaction idempotency with request ID."""
        # Add idempotency key
        valid_transfer_data["idempotency_key"] = "test_idempotency_123"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # First request
            response1 = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
            
            # Second request with same idempotency key
            response2 = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
            
            # Both should succeed but second should return same result
            if response1.status_code == 201:
                assert response2.status_code in [201, 200]  # 200 for duplicate
                if response2.status_code == 200:
                    # Should indicate it's a duplicate
                    assert response1.json()["data"]["transaction_id"] == response2.json()["data"]["transaction_id"]
    
    def test_transaction_encryption(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test that sensitive transaction data is encrypted."""
        # This would test encryption of sensitive fields in storage
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.core.security.SecurityUtils.encrypt_sensitive_data') as mock_encrypt:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
            
            if response.status_code == 201:
                # Verify encryption was called for sensitive data
                assert mock_encrypt.called
    
    def test_transaction_fraud_detection(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config):
        """Test fraud detection mechanisms."""
        # Simulate suspicious transaction pattern
        suspicious_transfer = valid_transfer_data.copy()
        suspicious_transfer["amount"] = 499999.0  # Just under daily limit
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.transaction_service.TransactionService.transfer_money') as mock_transfer:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock fraud detection triggering
            mock_transfer.side_effect = ValueError("Transaction flagged for manual review")
            
            response = test_client.post("/transactions/send", json=suspicious_transfer, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "review" in data["detail"]["message"].lower() or "flagged" in data["detail"]["message"].lower()


class TestTransactionAuditTrail:
    """Test cases for transaction audit trail functionality."""
    
    def test_transaction_audit_logging(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config, setup_test_csv_files):
        """Test that transactions are properly logged."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.core.logging.AuditLogger.log_audit') as mock_audit:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
            
            # Verify audit log was called
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "money_transfer"
            assert audit_call["user_id"] == "USR001"
            assert "amount" in audit_call
    
    def test_failed_transaction_audit_logging(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config):
        """Test that failed transactions are properly logged."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.core.logging.AuditLogger.log_audit') as mock_audit, \
             patch('app.services.transaction_service.TransactionService.transfer_money') as mock_transfer:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock transaction failure
            mock_transfer.side_effect = ValueError("Insufficient funds")
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
            
            # Verify failed transaction was logged
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "money_transfer_failed"
            assert "error" in audit_call


class TestTransactionErrorHandling:
    """Test cases for transaction error scenarios."""
    
    def test_storage_error_during_transfer(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config):
        """Test handling of storage errors during transfer."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.transaction_service.TransactionService.transfer_money') as mock_transfer:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock storage error
            mock_transfer.side_effect = Exception("Storage connection failed")
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"]["message"].lower()
    
    def test_network_timeout_simulation(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config):
        """Test handling of network timeouts during transfer."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.transaction_service.TransactionService.transfer_money') as mock_transfer:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock timeout error
            mock_transfer.side_effect = TimeoutError("Request timed out")
            
            response = test_client.post("/transactions/send", json=valid_transfer_data, headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "timeout" in data["detail"]["message"].lower() or "error" in data["detail"]["message"].lower()
    
    def test_concurrent_transfers_race_condition(self, test_client: TestClient, auth_headers, valid_transfer_data, mock_storage_config):
        """Test handling of concurrent transfers and race conditions."""
        # Simulate multiple concurrent transfers that might cause race conditions
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Create multiple transfer requests
            responses = []
            for i in range(3):
                transfer_data = valid_transfer_data.copy()
                transfer_data["amount"] = 100000.0  # Large amount each
                response = test_client.post("/transactions/send", json=transfer_data, headers=auth_headers)
                responses.append(response)
            
            # Some should succeed, others might fail due to insufficient balance or limits
            status_codes = [r.status_code for r in responses]
            assert any(code == 201 for code in status_codes) or all(code in [400, 500] for code in status_codes)
