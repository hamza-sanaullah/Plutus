#!/usr/bin/env python3
"""
Plutus Backend - Balance Check API Test
Simple test for the balance check endpoint only.

Team: Yay!
Date: August 30, 2025
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "USR737BE6D4"  # Valid user ID from CSV (hamza user)

async def test_balance_check_api():
    """Test only the balance check API endpoint."""
    print(f"🏦 Testing Balance Check API for User: {TEST_USER_ID}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test health check first
            print("🔍 Testing server health...")
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Server Status: {health_data.get('service')} is {health_data.get('status')}")
                else:
                    print(f"❌ Server health check failed: {response.status}")
                    return
            
            print("\n💰 Testing Balance Check Endpoint...")
            
            # Test balance check endpoint
            balance_url = f"{BASE_URL}/balance/current/{TEST_USER_ID}"
            print(f"🌐 Request URL: {balance_url}")
            
            async with session.get(balance_url) as response:
                print(f"📡 Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Balance Check SUCCESS!")
                    print("\n📊 Response Data:")
                    print(json.dumps(data, indent=2))
                    
                    # Extract balance information
                    if "data" in data and "current_balance" in data["data"]:
                        balance = data["data"]["current_balance"]
                        account_number = data["data"].get("account_number", "N/A")
                        daily_limit = data["data"].get("daily_limit", "N/A")
                        daily_spent = data["data"].get("daily_spent_today", "N/A")
                        available_limit = data["data"].get("available_daily_limit", "N/A")
                        
                        print(f"\n💵 Account Details:")
                        print(f"   User ID: {TEST_USER_ID}")
                        print(f"   Current Balance: PKR {balance}")
                        print(f"   Account Number: {account_number}")
                        print(f"   Daily Limit: PKR {daily_limit}")
                        print(f"   Daily Spent Today: PKR {daily_spent}")
                        print(f"   Available Daily Limit: PKR {available_limit}")
                        
                        print(f"\n🎉 Balance Check API is working perfectly!")
                        print(f"   The simplified API successfully returned balance for user {TEST_USER_ID}")
                    else:
                        print("⚠️  Response format unexpected - missing balance data")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Balance Check FAILED with status: {response.status}")
                    print(f"📄 Error Response: {error_text}")
                    
                    # Try to parse error as JSON
                    try:
                        error_data = json.loads(error_text)
                        if "detail" in error_data:
                            print(f"🔍 Error Details: {error_data['detail']}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✨ Balance Check API Test Complete")


async def main():
    """Main test runner."""
    print("Plutus Backend - Balance Check API Test")
    print("Testing simplified JWT-free balance endpoint")
    await test_balance_check_api()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
