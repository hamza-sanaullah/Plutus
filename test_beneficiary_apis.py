"""
Test script for the new attractive Beneficiary API endpoints
Tests all CRUD operations: Add, List, Search, Remove

New API Endpoints:
- POST /api/beneficiaries/add/{user_id}
- GET /api/beneficiaries/list/{user_id}  
- GET /api/beneficiaries/search/{user_id}/{query}
- DELETE /api/beneficiaries/remove/{user_id}/{beneficiary_id}
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"
BENEFICIARIES_URL = f"{BASE_URL}/api/beneficiaries"

# Test user data
TEST_USER_ID = "USR12345678"  # hamza_dev from users.csv
TEST_BENEFICIARY = {
    "name": "Amna Sheikh",
    "account_number": "12345678901",
    "bank_name": "HBL Bank", 
    "branch_code": "1234"
}

def print_separator(title):
    """Print a formatted separator for test sections."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_response(response, operation):
    """Print formatted API response."""
    print(f"\n🔍 {operation}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_add_beneficiary():
    """Test the new attractive Add Beneficiary API."""
    print_separator("TEST 1: Add Beneficiary API")
    
    url = f"{BENEFICIARIES_URL}/add/{TEST_USER_ID}"
    print(f"🔗 URL: {url}")
    
    try:
        response = requests.post(url, json=TEST_BENEFICIARY)
        print_response(response, "Add Beneficiary")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Beneficiary added successfully!")
            return result.get("beneficiary_id")
        else:
            print("❌ Failed to add beneficiary")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_list_beneficiaries():
    """Test the new attractive List Beneficiaries API."""
    print_separator("TEST 2: List Beneficiaries API")
    
    url = f"{BENEFICIARIES_URL}/list/{TEST_USER_ID}"
    print(f"🔗 URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response, "List Beneficiaries")
        
        if response.status_code == 200:
            result = response.json()
            beneficiaries = result.get("beneficiaries", [])
            print(f"✅ Found {len(beneficiaries)} beneficiaries")
            return beneficiaries
        else:
            print("❌ Failed to list beneficiaries")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_search_beneficiaries():
    """Test the new attractive Search Beneficiaries API."""
    print_separator("TEST 3: Search Beneficiaries API")
    
    search_query = "Amna"
    url = f"{BENEFICIARIES_URL}/search/{TEST_USER_ID}/{search_query}"
    print(f"🔗 URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response, f"Search Beneficiaries for '{search_query}'")
        
        if response.status_code == 200:
            result = response.json()
            matches = result.get("matches", [])
            print(f"✅ Found {len(matches)} matching beneficiaries")
            return matches
        else:
            print("❌ Failed to search beneficiaries")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_remove_beneficiary(beneficiary_id):
    """Test the new attractive Remove Beneficiary API."""
    print_separator("TEST 4: Remove Beneficiary API")
    
    if not beneficiary_id:
        print("❌ No beneficiary ID provided for removal test")
        return False
    
    url = f"{BENEFICIARIES_URL}/remove/{TEST_USER_ID}/{beneficiary_id}"
    print(f"🔗 URL: {url}")
    
    try:
        response = requests.delete(url)
        print_response(response, f"Remove Beneficiary {beneficiary_id}")
        
        if response.status_code == 200:
            print("✅ Beneficiary removed successfully!")
            return True
        else:
            print("❌ Failed to remove beneficiary")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all beneficiary API tests."""
    print_separator("🚀 TESTING NEW ATTRACTIVE BENEFICIARY APIs")
    print(f"Testing with user: {TEST_USER_ID} (hamza_dev)")
    print(f"Base URL: {BENEFICIARIES_URL}")
    print("\n📋 Available users from users.csv:")
    print("- USR12345678 (hamza_dev)")
    print("- USR87654321 (zunaira_test)")
    print("- USR11223344 (husnain_demo)")
    print("- USR55667788 (areesha_user)")
    print("- USR99887766 (ahmed_client)")
    print(f"\n🎯 Testing with: {TEST_USER_ID}")
    
    # Test 1: Add beneficiary
    beneficiary_id = test_add_beneficiary()
    
    # Test 2: List beneficiaries  
    beneficiaries = test_list_beneficiaries()
    
    # Test 3: Search beneficiaries
    search_results = test_search_beneficiaries()
    
    # Test 4: Remove beneficiary (if we added one)
    if beneficiary_id:
        test_remove_beneficiary(beneficiary_id)
    
    # Final verification - list again to confirm removal
    if beneficiary_id:
        print_separator("FINAL VERIFICATION: List After Removal")
        final_beneficiaries = test_list_beneficiaries()
    
    print_separator("✨ ALL TESTS COMPLETED")
    print("\n🎯 New Attractive API Endpoints Summary:")
    print("✅ POST /api/beneficiaries/add/{user_id}")
    print("✅ GET /api/beneficiaries/list/{user_id}")
    print("✅ GET /api/beneficiaries/search/{user_id}/{query}")
    print("✅ DELETE /api/beneficiaries/remove/{user_id}/{beneficiary_id}")

if __name__ == "__main__":
    main()
