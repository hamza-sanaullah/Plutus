"""
Plutus Backend - Beneficiary Management Tests
Comprehensive tests for beneficiary operations including CRUD and validation.

Team: Yay!
Date: August 30, 2025
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json


class TestBeneficiaryCreation:
    """Test cases for beneficiary creation functionality."""
    
    def test_add_beneficiary_success(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config, setup_test_csv_files):
        """Test successful beneficiary addition."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "beneficiary_id" in data["data"]
        assert data["data"]["account_number"] == valid_beneficiary_data["account_number"]
        assert data["data"]["name"] == valid_beneficiary_data["name"]
        assert data["data"]["bank_name"] == valid_beneficiary_data["bank_name"]
    
    def test_add_beneficiary_duplicate_account(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test adding beneficiary with duplicate account number."""
        # Use existing beneficiary account from setup data
        duplicate_beneficiary = {
            "account_number": "9876543210987654",  # Existing in setup
            "name": "Different Name",
            "bank_name": "HBL",
            "iban": "PK36HABB0123456789012345",
            "relationship": "friend",
            "nickname": "duplicate_test"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/beneficiaries/", json=duplicate_beneficiary, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()
    
    def test_add_beneficiary_invalid_account_number(self, test_client: TestClient, auth_headers, valid_beneficiary_data, invalid_data_samples):
        """Test adding beneficiary with invalid account number."""
        valid_beneficiary_data["account_number"] = invalid_data_samples["invalid_account"]
        
        response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "account number" in data["detail"].lower()
    
    def test_add_beneficiary_invalid_iban(self, test_client: TestClient, auth_headers, valid_beneficiary_data, invalid_data_samples):
        """Test adding beneficiary with invalid IBAN."""
        valid_beneficiary_data["iban"] = invalid_data_samples["invalid_iban"]
        
        response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "iban" in data["detail"].lower()
    
    def test_add_beneficiary_invalid_bank(self, test_client: TestClient, auth_headers, valid_beneficiary_data):
        """Test adding beneficiary with unsupported bank."""
        valid_beneficiary_data["bank_name"] = "INVALID_BANK"
        
        response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "bank" in data["detail"].lower()
    
    def test_add_beneficiary_missing_required_fields(self, test_client: TestClient, auth_headers):
        """Test adding beneficiary with missing required fields."""
        incomplete_data = {
            "account_number": "1234567890123456",
            "name": "Test User"
        }
        
        response = test_client.post("/beneficiaries/", json=incomplete_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_add_beneficiary_unauthorized(self, test_client: TestClient, valid_beneficiary_data):
        """Test adding beneficiary without authentication."""
        response = test_client.post("/beneficiaries/", json=valid_beneficiary_data)
        
        assert response.status_code == 403
    
    def test_add_beneficiary_max_limit(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config):
        """Test adding beneficiary when maximum limit is reached."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.beneficiary_service.BeneficiaryService.add_beneficiary') as mock_add:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock service to return limit exceeded error
            mock_add.side_effect = ValueError("Maximum number of beneficiaries (50) reached")
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "maximum" in data["detail"].lower()


class TestBeneficiaryRetrieval:
    """Test cases for beneficiary retrieval functionality."""
    
    def test_get_all_beneficiaries_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful retrieval of all beneficiaries."""
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/beneficiaries/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"]["data"], list)
        
        # Verify beneficiary structure
        if data["data"]["data"]:
            beneficiary = data["data"]["data"][0]
            assert "beneficiary_id" in beneficiary
            assert "account_number" in beneficiary
            assert "name" in beneficiary
            assert "bank_name" in beneficiary
    
    def test_get_beneficiaries_with_pagination(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test beneficiary retrieval with pagination."""
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
            
            response = test_client.get("/beneficiaries/", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["data"]) <= 5
    
    def test_get_beneficiaries_with_search(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test beneficiary retrieval with search filter."""
        params = {
            "search": "Jane"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/beneficiaries/", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify search results contain the search term
        for beneficiary in data["data"]["data"]:
            assert "jane" in beneficiary["name"].lower()
    
    def test_get_beneficiaries_by_bank(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test beneficiary retrieval filtered by bank."""
        params = {
            "bank_name": "HBL"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get("/beneficiaries/", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify all results are from HBL
        for beneficiary in data["data"]["data"]:
            assert beneficiary["bank_name"] == "HBL"
    
    def test_get_single_beneficiary_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful retrieval of single beneficiary."""
        beneficiary_id = "BEN001"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["beneficiary_id"] == beneficiary_id
    
    def test_get_single_beneficiary_not_found(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test retrieval of non-existent beneficiary."""
        beneficiary_id = "NONEXISTENT"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.get(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestBeneficiaryUpdate:
    """Test cases for beneficiary update functionality."""
    
    def test_update_beneficiary_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful beneficiary update."""
        beneficiary_id = "BEN001"
        update_data = {
            "name": "Updated Name",
            "nickname": "updated_nick",
            "relationship": "spouse"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.put(f"/beneficiaries/{beneficiary_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == update_data["name"]
        assert data["data"]["nickname"] == update_data["nickname"]
        assert data["data"]["relationship"] == update_data["relationship"]
    
    def test_update_beneficiary_not_found(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test updating non-existent beneficiary."""
        beneficiary_id = "NONEXISTENT"
        update_data = {
            "name": "Updated Name"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.put(f"/beneficiaries/{beneficiary_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_update_beneficiary_unauthorized_user(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test updating beneficiary by unauthorized user."""
        beneficiary_id = "BEN001"
        update_data = {
            "name": "Updated Name"
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            # Different user trying to update
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR999",
                "email": "other@example.com"
            }
            
            response = test_client.put(f"/beneficiaries/{beneficiary_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "permission" in data["detail"].lower()
    
    def test_update_beneficiary_immutable_fields(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that immutable fields cannot be updated."""
        beneficiary_id = "BEN001"
        update_data = {
            "account_number": "9999999999999999",  # Should not be updatable
            "bank_name": "Different Bank",          # Should not be updatable
            "name": "Updated Name"      # Should be updatable
        }
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.put(f"/beneficiaries/{beneficiary_id}", json=update_data, headers=auth_headers)
        
        # Should succeed but immutable fields should not change
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == update_data["name"]
        # Account number and bank should remain unchanged
        assert data["data"]["account_number"] != update_data["account_number"]


class TestBeneficiaryDeletion:
    """Test cases for beneficiary deletion functionality."""
    
    def test_delete_beneficiary_success(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test successful beneficiary deletion."""
        beneficiary_id = "BEN001"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.delete(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()
    
    def test_delete_beneficiary_not_found(self, test_client: TestClient, auth_headers, mock_storage_config):
        """Test deleting non-existent beneficiary."""
        beneficiary_id = "NONEXISTENT"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.delete(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_delete_beneficiary_unauthorized_user(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test deleting beneficiary by unauthorized user."""
        beneficiary_id = "BEN001"
        
        with patch('app.core.security.get_security_manager') as mock_security:
            # Different user trying to delete
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR999",
                "email": "other@example.com"
            }
            
            response = test_client.delete(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "permission" in data["detail"].lower()
    
    def test_delete_beneficiary_with_pending_transactions(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test deleting beneficiary with pending transactions."""
        beneficiary_id = "BEN001"
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.beneficiary_service.BeneficiaryService.delete_beneficiary') as mock_delete:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock service to return pending transactions error
            mock_delete.side_effect = ValueError("Cannot delete beneficiary with pending transactions")
            
            response = test_client.delete(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "pending" in data["detail"].lower()


class TestBeneficiaryValidation:
    """Test cases for beneficiary validation business rules."""
    
    def test_self_beneficiary_prevention(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config, setup_test_csv_files):
        """Test prevention of adding self as beneficiary."""
        # Use same account number as the user's own account
        valid_beneficiary_data["account_number"] = "0123456789012345"  # User's own account from setup
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "yourself" in data["detail"].lower() or "self" in data["detail"].lower()
    
    def test_beneficiary_account_validation_with_bank(self, test_client: TestClient, auth_headers, valid_beneficiary_data):
        """Test that account number validation considers the bank."""
        # HBL account number with UBL bank should fail
        valid_beneficiary_data["account_number"] = "0011234567890123"  # HBL format
        valid_beneficiary_data["bank_name"] = "UBL"  # Different bank
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "account number" in data["detail"].lower() and "bank" in data["detail"].lower()
    
    def test_beneficiary_nickname_uniqueness(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config, setup_test_csv_files):
        """Test that beneficiary nicknames must be unique per user."""
        # Use existing nickname from setup data
        valid_beneficiary_data["nickname"] = "jane_friend"  # Existing nickname
        
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "nickname" in data["detail"].lower() and "exists" in data["detail"].lower()


class TestBeneficiaryAuditTrail:
    """Test cases for beneficiary audit trail functionality."""
    
    def test_beneficiary_add_audit_logging(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config, setup_test_csv_files):
        """Test that beneficiary additions are properly logged."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.base_service.BaseService.log_audit') as mock_audit:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
            
            # Verify audit log was called
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "beneficiary_added"
            assert audit_call["user_id"] == "USR001"
    
    def test_beneficiary_update_audit_logging(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that beneficiary updates are properly logged."""
        beneficiary_id = "BEN001"
        update_data = {"name": "Updated Name"}
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.base_service.BaseService.log_audit') as mock_audit:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.put(f"/beneficiaries/{beneficiary_id}", json=update_data, headers=auth_headers)
            
            # Verify audit log was called
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "beneficiary_updated"
            assert audit_call["user_id"] == "USR001"
    
    def test_beneficiary_delete_audit_logging(self, test_client: TestClient, auth_headers, mock_storage_config, setup_test_csv_files):
        """Test that beneficiary deletions are properly logged."""
        beneficiary_id = "BEN001"
        
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.base_service.BaseService.log_audit') as mock_audit:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            response = test_client.delete(f"/beneficiaries/{beneficiary_id}", headers=auth_headers)
            
            # Verify audit log was called
            assert mock_audit.called
            audit_call = mock_audit.call_args[1]
            assert audit_call["action"] == "beneficiary_removed"
            assert audit_call["user_id"] == "USR001"


class TestBeneficiaryErrorHandling:
    """Test cases for beneficiary error scenarios."""
    
    def test_storage_error_handling(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config):
        """Test handling of storage errors during beneficiary operations."""
        with patch('app.core.security.get_security_manager') as mock_security, \
             patch('app.services.beneficiary_service.BeneficiaryService.add_beneficiary') as mock_add:
            
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Mock storage error
            mock_add.side_effect = Exception("Storage connection failed")
            
            response = test_client.post("/beneficiaries/", json=valid_beneficiary_data, headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_concurrent_beneficiary_operations(self, test_client: TestClient, auth_headers, valid_beneficiary_data, mock_storage_config):
        """Test handling of concurrent beneficiary operations."""
        # Test adding same beneficiary concurrently
        with patch('app.core.security.get_security_manager') as mock_security:
            mock_security.return_value.verify_access_token.return_value = {
                "valid": True,
                "user_id": "USR001",
                "email": "john@example.com"
            }
            
            # Simulate multiple concurrent requests
            responses = []
            for i in range(3):
                beneficiary_data = valid_beneficiary_data.copy()
                beneficiary_data["nickname"] = f"concurrent_test_{i}"
                response = test_client.post("/beneficiaries/", json=beneficiary_data, headers=auth_headers)
                responses.append(response)
            
            # At least one should succeed, others might fail due to duplicate account
            success_count = sum(1 for r in responses if r.status_code == 201)
            assert success_count >= 1
