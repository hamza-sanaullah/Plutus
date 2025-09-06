# API functions for Plutus Banking Assistant

import requests
import json
from datetime import datetime
import streamlit as st
from config import API_URL, API_TIMEOUT

def call_chatbot_api(message):
    """Function to call chatbot API"""
    headers = {
        "Content-Type": "application/json"
    }
    
    # Build history string with user and bot messages
    history_list = []
    try:
        current_chat = st.session_state.chats.get(st.session_state.current_chat, [])
        user_msg_count = sum(1 for msg in current_chat if msg.get("role") == "user")
        if user_msg_count > 1:
            for msg in current_chat[:-1]:
                if msg.get("role") == "user":
                    history_list.append(f"User: {msg['content']}")
                elif msg.get("role") == "bot":
                    history_list.append(f"Bot: {msg['content']}")
    except Exception:
        history_list = []
    
    payload = {"query": message, "history": history_list}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "reply": f"Sorry, I'm experiencing technical difficulties. Please try again. Error: {str(e)}"
        }

def mock_chatbot_api(user_message):
    """Mock API function for testing"""
    import time
    time.sleep(2)  # Simulate API delay
    
    user_message_lower = user_message.lower()
    
    if any(keyword in user_message_lower for keyword in ['balance', 'account balance', 'how much']):
        return {
            "reply": "Your current account balance is $2,847.56. Your savings account has $15,230.00. Is there anything else I can help you with?"
        }
    elif any(keyword in user_message_lower for keyword in ['send', 'transfer', 'pay']):
        return {
            "reply": "Transfer completed successfully! The money has been sent. Transaction ID: TXN" + datetime.now().strftime('%Y%m%d%H%M%S')
        }
    elif any(keyword in user_message_lower for keyword in ['help', 'what can you do']):
        return {
            "reply": "I'm Plutus, your AI banking assistant! I can help you with:\n\n• Check account balances 💳\n• Transfer money 💸\n• Add beneficiaries 👥\n• Generate statements 📄\n• View transaction history 📊\n\nJust tell me what you'd like to do!"
        }
    else:
        return {
            "reply": "I understand you're looking for banking assistance. Could you please clarify what you'd like me to help you with? I can check balances, transfer money, add beneficiaries, or provide statements."
        }
