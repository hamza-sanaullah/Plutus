"""
Plutus Backend - Integration Tests
End-to-end integration tests for complete banking workflows.

Team: Yay!
Date: August 30, 2025
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import time


class TestCompleteUserJourney:
    """Test complete user journey from registration to transactions."""
    
    def test_full_user_workflow(self, test_client: TestClient, mock_storage_config, setup_test_csv_files):
        """Test complete user workflow: register -> login -> add beneficiary -> transfer money."""
        
        # Step 1: User Registration
        registration_data = {
            "full_name": "Integration Test User",
            "email": "integration@test.com",
            "password": "IntegrationTest123!",
            "confirm_password": "IntegrationTest123!",
            "phone_number": "+923001234567",
            "account_number": "1111222233334444",
            "bank_name": "HBL",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street, Karachi",
            "cnic": "12345-6789012-3"
        }
        
        with patch('app.core.security.SecurityUtils.get_password_hash', return_value="hashed_password"):
            registration_response = test_client.post("/auth/register", json=registration_data)
        
        assert registration_response.status_code == 201
        user_data = registration_response.json()["data"]
        
        # Step 2: User Login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        with patch('app.core.security.SecurityUtils.verify_password', return_value=True), \
             patch('app.core.security.SecurityUtils.create_access_token', return_value="mock_access_token"), \
             patch('app.core.security.SecurityUtils.create_refresh_token', return_value="mock_refresh_token"):
            
            login_response = test_client.post("/auth/login", json=login_data)
        
        assert login_response.status_code == 200
        auth_data = login_response.json()["data"]
        auth_headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Step 3: Check Initial Balance
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": user_data["user_id"],
                "email": registration_data["email"]
            }
            
            balance_response = test_client.get("/balance/current", headers=auth_headers)
        
        assert balance_response.status_code == 200
        initial_balance = balance_response.json()["data"]["balance"]
        
        # Step 4: Add Beneficiary
        beneficiary_data = {
            "account_number": "5555666677778888",
            "beneficiary_name": "Integration Beneficiary",
            "bank_name": "UBL",
            "iban": "PK36UNIL0123456789012345",
            "relationship": "friend",
            "nickname": "integration_ben"
        }
        
        beneficiary_response = test_client.post("/beneficiaries/add", json=beneficiary_data, headers=auth_headers)
        
        assert beneficiary_response.status_code == 201
        beneficiary_id = beneficiary_response.json()["data"]["beneficiary_id"]
        
        # Step 5: Transfer Money
        transfer_data = {
            "beneficiary_id": beneficiary_id,
            "amount": 5000.0,
            "description": "Integration test transfer"
        }
        
        transfer_response = test_client.post("/transactions/transfer", json=transfer_data, headers=auth_headers)
        
        assert transfer_response.status_code == 201
        transaction_data = transfer_response.json()["data"]
        
        # Step 6: Verify Updated Balance
        updated_balance_response = test_client.get("/balance/current", headers=auth_headers)
        assert updated_balance_response.status_code == 200
        new_balance = updated_balance_response.json()["data"]["balance"]
        
        # Balance should be reduced by transfer amount
        expected_balance = initial_balance - transfer_data["amount"]
        assert abs(new_balance - expected_balance) < 0.01  # Allow for floating point precision
        
        # Step 7: Check Transaction History
        history_response = test_client.get("/transactions/history", headers=auth_headers)
        assert history_response.status_code == 200
        
        transactions = history_response.json()["data"]["transactions"]
        assert len(transactions) > 0
        
        # Find our transaction
        our_transaction = next((t for t in transactions if t["transaction_id"] == transaction_data["transaction_id"]), None)
        assert our_transaction is not None
        assert our_transaction["amount"] == transfer_data["amount"]
        assert our_transaction["status"] == "completed"
    
    def test_user_workflow_with_errors(self, test_client: TestClient, mock_storage_config, setup_test_csv_files):
        """Test user workflow with various error scenarios."""
        
        # Step 1: Try to login with non-existent user
        login_data = {
            "email": "nonexistent@test.com",
            "password": "TestPassword123!"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 401
        
        # Step 2: Register user with invalid data
        invalid_registration = {
            "full_name": "Test User",
            "email": "invalid-email",  # Invalid email
            "password": "weak",        # Weak password
            "confirm_password": "different",  # Mismatched password
            "phone_number": "invalid",        # Invalid phone
            "account_number": "123",          # Invalid account number
            "bank_name": "UNKNOWN_BANK"       # Invalid bank
        }
        
        registration_response = test_client.post("/auth/register", json=invalid_registration)
        assert registration_response.status_code in [400, 422]
        
        # Step 3: Register valid user
        valid_registration = {
            "full_name": "Error Test User",
            "email": "errortest@test.com",
            "password": "ErrorTest123!",
            "confirm_password": "ErrorTest123!",
            "phone_number": "+923001234567",
            "account_number": "2222333344445555",
            "bank_name": "HBL",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street, Karachi",
            "cnic": "12345-6789012-3"
        }
        
        with patch('app.core.security.SecurityUtils.get_password_hash', return_value="hashed_password"):
            registration_response = test_client.post("/auth/register", json=valid_registration)
        
        assert registration_response.status_code == 201
        user_data = registration_response.json()["data"]
        
        # Step 4: Login successfully
        login_data = {
            "email": valid_registration["email"],
            "password": valid_registration["password"]
        }
        
        with patch('app.core.security.SecurityUtils.verify_password', return_value=True), \
             patch('app.core.security.SecurityUtils.create_access_token', return_value="mock_access_token"), \
             patch('app.core.security.SecurityUtils.create_refresh_token', return_value="mock_refresh_token"):
            
            login_response = test_client.post("/auth/login", json=login_data)
        
        assert login_response.status_code == 200
        auth_data = login_response.json()["data"]
        auth_headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": user_data["user_id"],
                "email": valid_registration["email"]
            }
            
            # Step 5: Try to add invalid beneficiary
            invalid_beneficiary = {
                "account_number": "invalid",
                "beneficiary_name": "",  # Empty name
                "bank_name": "UNKNOWN",
                "iban": "invalid_iban"
            }
            
            beneficiary_response = test_client.post("/beneficiaries/add", json=invalid_beneficiary, headers=auth_headers)
            assert beneficiary_response.status_code in [400, 422]
            
            # Step 6: Try to transfer to non-existent beneficiary
            invalid_transfer = {
                "beneficiary_id": "NONEXISTENT",
                "amount": 1000.0
            }
            
            transfer_response = test_client.post("/transactions/transfer", json=invalid_transfer, headers=auth_headers)
            assert transfer_response.status_code == 404


class TestChatbotIntegrationScenarios:
    """Test scenarios specifically for chatbot integration."""
    
    def test_chatbot_balance_inquiry_flow(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test balance inquiry flow that chatbot would use."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Chatbot: Get current balance
            balance_response = test_client.get("/balance/current", headers=auth_headers)
            assert balance_response.status_code == 200
            
            balance_data = balance_response.json()
            assert "balance" in balance_data["data"]
            assert "currency" in balance_data["data"]
            
            # Chatbot: Get account summary for more details
            summary_response = test_client.get("/balance/summary", headers=auth_headers)
            assert summary_response.status_code == 200
            
            summary_data = summary_response.json()
            assert "account_info" in summary_data["data"]
            assert "transaction_summary" in summary_data["data"]
    
    def test_chatbot_beneficiary_management_flow(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test beneficiary management flow for chatbot."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Chatbot: List all beneficiaries
            list_response = test_client.get("/beneficiaries/", headers=auth_headers)
            assert list_response.status_code == 200
            
            beneficiaries = list_response.json()["data"]["beneficiaries"]
            
            # Chatbot: Search for specific beneficiary
            search_response = test_client.get("/beneficiaries/?search=Jane", headers=auth_headers)
            assert search_response.status_code == 200
            
            search_results = search_response.json()["data"]["beneficiaries"]
            
            # Chatbot: Get details of specific beneficiary
            if beneficiaries:
                beneficiary_id = beneficiaries[0]["beneficiary_id"]
                detail_response = test_client.get(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
                assert detail_response.status_code == 200
    
    def test_chatbot_transfer_flow(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test money transfer flow for chatbot."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Chatbot: Check daily limits before transfer
            limits_response = test_client.get("/transactions/daily-limits", headers=auth_headers)
            assert limits_response.status_code == 200
            
            limits_data = limits_response.json()["data"]
            remaining_limit = limits_data["remaining_amount"]
            
            # Chatbot: Get beneficiaries for transfer options
            beneficiaries_response = test_client.get("/beneficiaries/", headers=auth_headers)
            assert beneficiaries_response.status_code == 200
            
            beneficiaries = beneficiaries_response.json()["data"]["beneficiaries"]
            
            if beneficiaries and remaining_limit > 1000:
                # Chatbot: Initiate transfer
                transfer_data = {
                    "beneficiary_id": beneficiaries[0]["beneficiary_id"],
                    "amount": min(1000.0, remaining_limit - 100),  # Safe amount
                    "description": "Chatbot initiated transfer"
                }
                
                transfer_response = test_client.post("/transactions/transfer", json=transfer_data, headers=auth_headers)
                
                if transfer_response.status_code == 201:
                    transaction_id = transfer_response.json()["data"]["transaction_id"]
                    
                    # Chatbot: Get transaction receipt
                    receipt_response = test_client.get(f"/transactions/{transaction_id}/receipt", headers=auth_headers)
                    assert receipt_response.status_code == 200
    
    def test_chatbot_transaction_history_flow(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test transaction history flow for chatbot."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Chatbot: Get recent transactions
            recent_response = test_client.get("/transactions/history?limit=5", headers=auth_headers)
            assert recent_response.status_code == 200
            
            recent_data = recent_response.json()["data"]
            
            # Chatbot: Get transactions for specific period
            params = {
                "start_date": "2024-08-01",
                "end_date": "2024-08-31",
                "limit": 10
            }
            
            period_response = test_client.get("/transactions/history", headers=auth_headers, params=params)
            assert period_response.status_code == 200
            
            # Chatbot: Get specific transaction details
            transactions = recent_data["transactions"]
            if transactions:
                transaction_id = transactions[0]["transaction_id"]
                detail_response = test_client.get(f"/transactions/{transaction_id}", headers=auth_headers)
                assert detail_response.status_code == 200


class TestErrorRecoveryScenarios:
    """Test error recovery and resilience scenarios."""
    
    def test_authentication_token_expiry_recovery(self, test_client: TestClient, mock_storage_config, setup_test_csv_files):
        """Test recovery from expired authentication tokens."""
        
        # Step 1: Login to get tokens
        login_data = {
            "email": "john@example.com",
            "password": "TestPassword123!"
        }
        
        with patch('app.core.security.SecurityUtils.verify_password', return_value=True), \
             patch('app.core.security.SecurityUtils.create_access_token', return_value="mock_access_token"), \
             patch('app.core.security.SecurityUtils.create_refresh_token', return_value="mock_refresh_token"):
            
            login_response = test_client.post("/auth/login", json=login_data)
        
        assert login_response.status_code == 200
        auth_data = login_response.json()["data"]
        
        # Step 2: Use expired access token
        expired_headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        with patch('app.core.security.get_security_manager') as mock_security:
            # Mock expired token
            mock_security.return_value.verify_access_token.return_value = {
                "valid": False,
                "error": "Token expired"
            }
            
            balance_response = test_client.get("/balance/current", headers=expired_headers)
            assert balance_response.status_code == 401
        
        # Step 3: Refresh token
        refresh_data = {
            "refresh_token": auth_data["refresh_token"]
        }
        
        with patch('app.core.security.SecurityUtils.verify_refresh_token', return_value={"valid": True, "user_id": "USR001", "email": "john@example.com"}), \
             patch('app.core.security.SecurityUtils.create_access_token', return_value="new_access_token"):
            
            refresh_response = test_client.post("/auth/refresh", json=refresh_data)
        
        assert refresh_response.status_code == 200
        new_auth_data = refresh_response.json()["data"]
        
        # Step 4: Use new access token
        new_headers = {"Authorization": f"Bearer {new_auth_data['access_token']}"}
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            balance_response = test_client.get("/balance/current", headers=new_headers)
            assert balance_response.status_code == 200
    
    def test_partial_transaction_failure_recovery(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test recovery from partial transaction failures."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Step 1: Get initial balance
            balance_response = test_client.get("/balance/current", headers=auth_headers)
            assert balance_response.status_code == 200
            initial_balance = balance_response.json()["data"]["balance"]
            
            # Step 2: Attempt transfer that might fail
            transfer_data = {
                "beneficiary_id": "BEN001",
                "amount": 5000.0,
                "description": "Test partial failure"
            }
            
            with patch('app.services.transaction_service.TransactionService.transfer_money') as mock_transfer:
                # Mock partial failure (transaction created but not completed)
                mock_transfer.side_effect = Exception("Network error during processing")
                
                transfer_response = test_client.post("/transactions/transfer", json=transfer_data, headers=auth_headers)
                assert transfer_response.status_code == 500
            
            # Step 3: Verify balance unchanged after failed transaction
            balance_response = test_client.get("/balance/current", headers=auth_headers)
            assert balance_response.status_code == 200
            current_balance = balance_response.json()["data"]["balance"]
            
            # Balance should be unchanged
            assert abs(current_balance - initial_balance) < 0.01
    
    def test_concurrent_user_operations(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test concurrent operations by same user."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Simulate concurrent requests
            responses = []
            
            # Multiple balance inquiries
            for _ in range(3):
                response = test_client.get("/balance/current", headers=auth_headers)
                responses.append(response)
            
            # Multiple beneficiary listings
            for _ in range(3):
                response = test_client.get("/beneficiaries/", headers=auth_headers)
                responses.append(response)
            
            # Multiple transaction history requests
            for _ in range(3):
                response = test_client.get("/transactions/history", headers=auth_headers)
                responses.append(response)
            
            # All should succeed (no conflicts for read operations)
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count >= len(responses) * 0.8  # At least 80% should succeed


class TestDataConsistencyScenarios:
    """Test data consistency across operations."""
    
    def test_balance_consistency_after_transactions(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that balance remains consistent after multiple transactions."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Get initial balance
            balance_response = test_client.get("/balance/current", headers=auth_headers)
            assert balance_response.status_code == 200
            initial_balance = balance_response.json()["data"]["balance"]
            
            # Perform multiple small transactions
            transaction_amounts = [100.0, 250.0, 500.0]
            successful_transfers = []
            
            for amount in transaction_amounts:
                transfer_data = {
                    "beneficiary_id": "BEN001",
                    "amount": amount,
                    "description": f"Consistency test {amount}"
                }
                
                response = test_client.post("/transactions/transfer", json=transfer_data, headers=auth_headers)
                if response.status_code == 201:
                    successful_transfers.append(amount)
            
            # Get final balance
            final_balance_response = test_client.get("/balance/current", headers=auth_headers)
            assert final_balance_response.status_code == 200
            final_balance = final_balance_response.json()["data"]["balance"]
            
            # Calculate expected balance
            total_transferred = sum(successful_transfers)
            expected_balance = initial_balance - total_transferred
            
            # Verify consistency (allowing for small floating point differences)
            assert abs(final_balance - expected_balance) < 0.01
    
    def test_transaction_history_consistency(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that transaction history is consistent across different queries."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Get all transactions
            all_response = test_client.get("/transactions/history", headers=auth_headers)
            assert all_response.status_code == 200
            all_transactions = all_response.json()["data"]["transactions"]
            
            # Get transactions with pagination
            page1_response = test_client.get("/transactions/history?limit=5&offset=0", headers=auth_headers)
            assert page1_response.status_code == 200
            page1_transactions = page1_response.json()["data"]["transactions"]
            
            page2_response = test_client.get("/transactions/history?limit=5&offset=5", headers=auth_headers)
            assert page2_response.status_code == 200
            page2_transactions = page2_response.json()["data"]["transactions"]
            
            # Combine paginated results
            paginated_transactions = page1_transactions + page2_transactions
            
            # Verify consistency (at least the first 10 should match)
            min_length = min(len(all_transactions), len(paginated_transactions), 10)
            for i in range(min_length):
                assert all_transactions[i]["transaction_id"] == paginated_transactions[i]["transaction_id"]


class TestSystemLimitsAndBoundaries:
    """Test system limits and boundary conditions."""
    
    def test_maximum_beneficiaries_limit(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test maximum number of beneficiaries per user."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Try to add many beneficiaries
            successful_adds = 0
            max_attempts = 55  # Beyond typical limit of 50
            
            for i in range(max_attempts):
                beneficiary_data = {
                    "account_number": f"9999{i:012d}",  # Unique account numbers
                    "beneficiary_name": f"Test Beneficiary {i}",
                    "bank_name": "HBL",
                    "iban": f"PK36HABB{i:016d}",
                    "relationship": "friend",
                    "nickname": f"test_ben_{i}"
                }
                
                response = test_client.post("/beneficiaries/add", json=beneficiary_data, headers=auth_headers)
                
                if response.status_code == 201:
                    successful_adds += 1
                elif response.status_code == 400 and "maximum" in response.json()["detail"]["message"].lower():
                    # Hit the limit
                    break
            
            # Should have hit some reasonable limit
            assert successful_adds <= 50  # Assuming 50 is the limit
    
    def test_daily_transaction_limit_enforcement(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test daily transaction limit enforcement."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Check current daily limit usage
            limits_response = test_client.get("/transactions/daily-limits", headers=auth_headers)
            assert limits_response.status_code == 200
            
            limits_data = limits_response.json()["data"]
            remaining_limit = limits_data["remaining_amount"]
            
            if remaining_limit > 10000:
                # Try to transfer amount that would exceed daily limit
                transfer_data = {
                    "beneficiary_id": "BEN001",
                    "amount": remaining_limit + 1000,  # Exceed limit
                    "description": "Limit test transfer"
                }
                
                response = test_client.post("/transactions/transfer", json=transfer_data, headers=auth_headers)
                
                # Should be rejected due to limit
                assert response.status_code == 400
                assert "limit" in response.json()["detail"]["message"].lower()
    
    def test_extreme_amount_handling(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test handling of extreme transaction amounts."""
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            extreme_amounts = [
                0.001,      # Very small amount
                999999999,  # Very large amount
                -1000,      # Negative amount
                float('inf'),  # Infinity
            ]
            
            for amount in extreme_amounts:
                transfer_data = {
                    "beneficiary_id": "BEN001",
                    "amount": amount,
                    "description": f"Extreme amount test: {amount}"
                }
                
                try:
                    response = test_client.post("/transactions/transfer", json=transfer_data, headers=auth_headers)
                    # Should be rejected with appropriate error
                    assert response.status_code in [400, 422]
                except (ValueError, OverflowError):
                    # JSON serialization might fail for extreme values
                    pass
