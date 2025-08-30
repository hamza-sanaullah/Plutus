"""
Plutus Backend - Test Configuration
Test settings and fixtures for comprehensive API testing.

Team: Yay!
Date: August 30, 2025
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from typing import Dict, Any, Generator
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd

from app.main import app
from app.core.config import get_settings
from app.storage import get_storage_manager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(scope="function")
def temp_data_dir():
    """Create a temporary directory for test data files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def mock_storage_config(temp_data_dir):
    """Mock storage configuration to use temporary directory."""
    test_config = {
        "local_data_path": temp_data_dir,
        "users_csv": os.path.join(temp_data_dir, "users.csv"),
        "beneficiaries_csv": os.path.join(temp_data_dir, "beneficiaries.csv"),
        "transactions_csv": os.path.join(temp_data_dir, "transactions.csv"),
        "audit_logs_csv": os.path.join(temp_data_dir, "audit_logs.csv"),
    }
    
    # Patch the settings attributes directly - only fields that exist in Settings
    settings_obj = get_settings()
    original_attrs = {}
    
    for key, value in test_config.items():
        if hasattr(settings_obj, key):
            original_attrs[key] = getattr(settings_obj, key)
            setattr(settings_obj, key, value)
    
    yield test_config
    
    # Restore original attributes
    for key, value in original_attrs.items():
        setattr(settings_obj, key, value)


@pytest.fixture(scope="function")
def setup_test_csv_files(temp_data_dir):
    """Create test CSV files with sample data."""
    
    # Users CSV
    users_data = [
        {
            "user_id": "USR001",
            "username": "john",
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+923001234567",
            "account_number": "1234567890123456",
            "bank_name": "HBL",
            "hashed_password": "$2b$12$test_hash",
            "balance": 10000.0,
            "daily_transfer_limit": 50000.0,
            "daily_transferred_amount": 0.0,
            "daily_transaction_count": 0,
            "daily_transfer_date": "2025-08-30",
            "created_at": "2025-08-30T10:00:00Z",
            "updated_at": "2025-08-30T10:00:00Z"
        },
        {
            "user_id": "USR002",
            "username": "jane",
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "phone_number": "+923001234568",
            "account_number": "1234567890123457",
            "bank_name": "UBL",
            "hashed_password": "$2b$12$test_hash2",
            "balance": 15000.0,
            "daily_transfer_limit": 50000.0,
            "daily_transferred_amount": 0.0,
            "daily_transaction_count": 0,
            "daily_transfer_date": "2025-08-30",
            "created_at": "2025-08-30T10:00:00Z",
            "updated_at": "2025-08-30T10:00:00Z"
        }
    ]
    
    users_df = pd.DataFrame(users_data)
    users_df.to_csv(os.path.join(temp_data_dir, "users.csv"), index=False)
    
    # Beneficiaries CSV
    beneficiaries_data = [
        {
            "owner_user_id": "USR001",
            "beneficiary_id": "BEN001",
            "name": "Alice Cooper",
            "bank_name": "MCB",
            "account_number": "9876543210987654",
            "added_at": "2025-08-30T10:00:00Z"
        },
        {
            "owner_user_id": "USR001",
            "beneficiary_id": "BEN002",
            "name": "Bob Wilson",
            "bank_name": "NBP",
            "account_number": "9876543210987655",
            "added_at": "2025-08-30T10:00:00Z"
        }
    ]
    
    beneficiaries_df = pd.DataFrame(beneficiaries_data)
    beneficiaries_df.to_csv(os.path.join(temp_data_dir, "beneficiaries.csv"), index=False)
    
    # Transactions CSV (empty initially)
    transactions_df = pd.DataFrame(columns=[
        "transaction_id", "sender_user_id", "sender_name", "sender_account",
        "beneficiary_id", "beneficiary_name", "beneficiary_account", "beneficiary_bank",
        "amount", "transaction_fee", "total_amount", "description", "status",
        "created_at", "completed_at", "failure_reason"
    ])
    transactions_df.to_csv(os.path.join(temp_data_dir, "transactions.csv"), index=False)
    
    # Audit logs CSV (empty initially)
    audit_df = pd.DataFrame(columns=[
        "log_id", "user_id", "action", "details", "timestamp", "ip_address", "request_id"
    ])
    audit_df.to_csv(os.path.join(temp_data_dir, "audit_logs.csv"), index=False)
    
    return {
        "users": users_data,
        "beneficiaries": beneficiaries_data
    }


@pytest.fixture(scope="function")
def valid_user_token(test_client, setup_test_csv_files, mock_storage_config):
    """Generate a valid JWT token for testing authenticated endpoints."""
    login_data = {
        "username": "john",
        "password": "TestPassword123!"
    }
    
    # Mock the password verification to return True
    with patch('app.core.security.SecurityUtils.verify_password', return_value=True):
        response = test_client.post("/auth/login", json=login_data)
        
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    else:
        # Return a mock token for testing
        return "mock_jwt_token_for_testing"


@pytest.fixture(scope="function")
def auth_headers(valid_user_token):
    """Create authorization headers with valid token."""
    return {"Authorization": f"Bearer {valid_user_token}"}


# Test data fixtures
@pytest.fixture
def valid_registration_data():
    """Valid user registration data for testing."""
    return {
        "username": "testuser",
        "password": "TestPassword123!",
        "account_number": "1234567890123458",
        "initial_balance": 5000.0,
        "daily_limit": 15000.0
    }


@pytest.fixture
def valid_login_data():
    """Valid user login data for testing."""
    return {
        "username": "testuser",
        "password": "TestPassword123!"
    }


@pytest.fixture
def valid_beneficiary_data():
    """Valid beneficiary data for testing."""
    return {
        "name": "Test Beneficiary",
        "bank_name": "BAFL",
        "account_number": "1111222233334444"
    }


@pytest.fixture
def valid_transaction_data():
    """Valid transaction data for testing."""
    return {
        "beneficiary_id": "BEN001",
        "amount": 1000.0,
        "description": "Test transfer"
    }


@pytest.fixture
def valid_transfer_data():
    """Valid transfer data for testing."""
    return {
        "beneficiary_id": "BEN001",
        "amount": 1000.0,
        "description": "Test transfer to beneficiary"
    }


@pytest.fixture
def invalid_data_samples():
    """Collection of invalid data for negative testing."""
    return {
        "invalid_email": "not_an_email",
        "weak_password": "123",
        "invalid_phone": "123456",
        "invalid_account": "123",
        "invalid_iban": "INVALID_IBAN",
        "negative_amount": -100.0,
        "excessive_amount": 600000.0,
        "empty_string": "",
        "none_value": None
    }


# Utility functions for tests
def create_test_user(client: TestClient, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to create a test user."""
    response = client.post("/auth/register", json=user_data)
    return response.json()


def login_test_user(client: TestClient, login_data: Dict[str, Any]) -> str:
    """Helper function to login and get access token."""
    response = client.post("/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    return None


def add_test_beneficiary(client: TestClient, beneficiary_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Helper function to add a test beneficiary."""
    response = client.post("/beneficiaries/", json=beneficiary_data, headers=headers)
    return response.json()


def send_test_transaction(client: TestClient, transaction_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Helper function to send a test transaction."""
    response = client.post("/transactions/send", json=transaction_data, headers=headers)
    return response.json()
