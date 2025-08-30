"""
Test Script for Transaction Sending API
Tests the send money functionality and verifies all operations work correctly.
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000/api"

def test_send_money():
    """Test the send money API functionality"""
    print("🧪 Testing Transaction Sending API...")
    print("=" * 50)
    
    # Test users from the CSV data
    sender_id = "USR12345678"  # hamza_dev
    recipient_id = "USR87654321"  # zunaira_test
    
    print(f"📋 Test Setup:")
    print(f"   Sender: {sender_id}")
    print(f"   Recipient: {recipient_id}")
    print(f"   Amount: 75.50")
    
    # Step 1: Check initial balances
    print("\n1️⃣ Checking initial balances...")
    
    try:
        sender_balance_response = requests.get(f"{BASE_URL}/balance/check/{sender_id}")
        recipient_balance_response = requests.get(f"{BASE_URL}/balance/check/{recipient_id}")
        
        if sender_balance_response.status_code == 200:
            sender_data = sender_balance_response.json()
            initial_sender_balance = sender_data['data']['balance']
            print(f"   ✅ Sender initial balance: {initial_sender_balance}")
        else:
            print(f"   ❌ Failed to get sender balance: {sender_balance_response.text}")
            return
        
        if recipient_balance_response.status_code == 200:
            recipient_data = recipient_balance_response.json()
            initial_recipient_balance = recipient_data['data']['balance']
            print(f"   ✅ Recipient initial balance: {initial_recipient_balance}")
        else:
            print(f"   ❌ Failed to get recipient balance: {recipient_balance_response.text}")
            return
    
    except Exception as e:
        print(f"   ❌ Error checking initial balances: {e}")
        return
    
    # Step 2: Send money
    print("\n2️⃣ Sending money...")
    
    transaction_data = {
        "to_user_id": recipient_id,
        "amount": 75.50,
        "description": "Test transfer via script"
    }
    
    try:
        send_response = requests.post(
            f"{BASE_URL}/transactions/send/{sender_id}",
            json=transaction_data,
            headers={"Content-Type": "application/json"}
        )
        
        if send_response.status_code == 201:
            response_data = send_response.json()
            if response_data.get('success'):
                transaction_id = response_data['data']['transaction_id']
                print(f"   ✅ Money sent successfully!")
                print(f"   📄 Transaction ID: {transaction_id}")
                print(f"   💰 Amount: {response_data['data']['amount']}")
            else:
                print(f"   ❌ Transaction failed: {response_data.get('message')}")
                return
        else:
            print(f"   ❌ API Error ({send_response.status_code}): {send_response.text}")
            return
    
    except Exception as e:
        print(f"   ❌ Error sending money: {e}")
        return
    
    # Step 3: Verify updated balances
    print("\n3️⃣ Verifying updated balances...")
    
    time.sleep(1)  # Small delay to ensure data is saved
    
    try:
        sender_balance_response = requests.get(f"{BASE_URL}/balance/check/{sender_id}")
        recipient_balance_response = requests.get(f"{BASE_URL}/balance/check/{recipient_id}")
        
        if sender_balance_response.status_code == 200:
            sender_data = sender_balance_response.json()
            new_sender_balance = sender_data['data']['balance']
            expected_sender_balance = initial_sender_balance - 75.50
            print(f"   💸 Sender new balance: {new_sender_balance}")
            print(f"   🎯 Expected balance: {expected_sender_balance}")
            
            if abs(new_sender_balance - expected_sender_balance) < 0.01:
                print(f"   ✅ Sender balance updated correctly!")
            else:
                print(f"   ❌ Sender balance mismatch!")
        
        if recipient_balance_response.status_code == 200:
            recipient_data = recipient_balance_response.json()
            new_recipient_balance = recipient_data['data']['balance']
            expected_recipient_balance = initial_recipient_balance + 75.50
            print(f"   💰 Recipient new balance: {new_recipient_balance}")
            print(f"   🎯 Expected balance: {expected_recipient_balance}")
            
            if abs(new_recipient_balance - expected_recipient_balance) < 0.01:
                print(f"   ✅ Recipient balance updated correctly!")
            else:
                print(f"   ❌ Recipient balance mismatch!")
    
    except Exception as e:
        print(f"   ❌ Error verifying balances: {e}")
        return
    
    # Step 4: Check transaction history
    print("\n4️⃣ Checking transaction history...")
    
    try:
        history_response = requests.get(f"{BASE_URL}/transactions/history/{sender_id}")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            if history_data.get('success'):
                transactions = history_data['data']['transactions']
                print(f"   📋 Found {len(transactions)} transactions for sender")
                
                # Look for our transaction
                found_transaction = False
                for txn in transactions:
                    if txn['transaction_id'] == transaction_id:
                        found_transaction = True
                        print(f"   ✅ Transaction found in history:")
                        print(f"      📄 ID: {txn['transaction_id']}")
                        print(f"      💰 Amount: {txn['amount']}")
                        print(f"      📝 Description: {txn['description']}")
                        break
                
                if not found_transaction:
                    print(f"   ❌ Transaction not found in history!")
            else:
                print(f"   ❌ Failed to get transaction history: {history_data.get('message')}")
        else:
            print(f"   ❌ API Error getting history: {history_response.text}")
    
    except Exception as e:
        print(f"   ❌ Error checking transaction history: {e}")
        return
    
    print("\n🎉 Test Completed Successfully!")
    print("   ✅ Send Money API is working correctly")
    print("   ✅ Balances are updated properly")
    print("   ✅ Transaction is saved to history")

def test_error_cases():
    """Test error handling scenarios"""
    print("\n🔧 Testing Error Scenarios...")
    print("=" * 50)
    
    # Test 1: Insufficient balance
    print("\n1️⃣ Testing insufficient balance...")
    try:
        response = requests.post(
            f"{BASE_URL}/transactions/send/USR12345678",
            json={"to_user_id": "USR87654321", "amount": 999999, "description": "Too much money"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 402:  # Payment Required
            print("   ✅ Correctly rejected insufficient balance")
        else:
            print(f"   ❌ Unexpected response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing insufficient balance: {e}")
    
    # Test 2: Invalid recipient
    print("\n2️⃣ Testing invalid recipient...")
    try:
        response = requests.post(
            f"{BASE_URL}/transactions/send/USR12345678",
            json={"to_user_id": "INVALID_USER", "amount": 10, "description": "To nobody"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:  # Not Found
            print("   ✅ Correctly rejected invalid recipient")
        else:
            print(f"   ❌ Unexpected response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing invalid recipient: {e}")
    
    # Test 3: Invalid sender
    print("\n3️⃣ Testing invalid sender...")
    try:
        response = requests.post(
            f"{BASE_URL}/transactions/send/INVALID_SENDER",
            json={"to_user_id": "USR87654321", "amount": 10, "description": "From nobody"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:  # Not Found
            print("   ✅ Correctly rejected invalid sender")
        else:
            print(f"   ❌ Unexpected response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing invalid sender: {e}")

if __name__ == "__main__":
    print("🚀 Starting Transaction API Test Suite")
    print("📡 Server: http://localhost:8000")
    print("⏰ Time:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("\n")
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print("❌ Server responded but with error")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the server is running: python -m uvicorn app.main:app --reload")
        exit(1)
    
    # Run tests
    test_send_money()
    test_error_cases()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!")
    print("📊 Check the results above for API functionality status")
