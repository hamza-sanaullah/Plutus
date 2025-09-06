# Utility functions for Plutus Banking Assistant

import streamlit as st
from datetime import datetime
from config import WELCOME_MESSAGES

def initialize_session_state():
    """Initialize session state variables"""
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    
    if "message_input" not in st.session_state:
        st.session_state.message_input = ""
    
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    if "selected_service" not in st.session_state:
        st.session_state.selected_service = None
    
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    
    if "welcome_message_index" not in st.session_state:
        st.session_state.welcome_message_index = 0

def create_new_chat():
    """Create a new chat session"""
    chat_count = len(st.session_state.chats) + 1
    chat_name = f"Chat {chat_count}"
    
    # Get rotating welcome message
    welcome_message = WELCOME_MESSAGES[st.session_state.welcome_message_index % len(WELCOME_MESSAGES)]
    st.session_state.welcome_message_index += 1
    
    st.session_state.chats[chat_name] = [
        {
            "role": "welcome", 
            "content": welcome_message, 
            "timestamp": datetime.now().strftime("%H:%M"), 
            "liked": None
        }
    ]
    
    st.session_state.current_chat = chat_name
    return chat_name

def get_current_placeholder():
    """Get the current input placeholder based on selected service"""
    if st.session_state.selected_service:
        from config import BANKING_SERVICES
        return BANKING_SERVICES[st.session_state.selected_service]["placeholder"]
    return "Ask anything about banking..."

def format_timestamp():
    """Get current timestamp in HH:MM format"""
    return datetime.now().strftime("%H:%M")

def get_service_description(service_key):
    """Get description for a banking service"""
    from config import BANKING_SERVICES
    return BANKING_SERVICES.get(service_key, {}).get("description", "")
