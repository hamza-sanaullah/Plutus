# Plutus Banking Assistant - Simple Working Version

import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Plutus - AI Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Chat 1": [
            {"role": "welcome", "content": "Hello! I'm Plutus, your AI-powered banking assistant. How can I help you with your banking needs today?", "timestamp": datetime.now().strftime("%H:%M")}
        ]
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Simple CSS - minimal changes
st.markdown("""
<style>
    .stButton > button {
        background: transparent !important;
        color: #1a1a1a !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 6px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        font-weight: 400 !important;
        width: 100% !important;
        text-align: left !important;
    }
    
    .stButton > button:hover {
        background: #f0f0f0 !important;
    }
    
    .stTextInput input {
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #007bff !important;
        box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Theme toggle
theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("## 🏦 Plutus")
    
    # New Chat Button
    if st.button("+ New Chat", key="new_chat", use_container_width=True):
        chat_count = len(st.session_state.chats) + 1
        chat_name = f"Chat {chat_count}"
        st.session_state.chats[chat_name] = [
            {"role": "welcome", "content": "Hello! I'm Plutus, your AI-powered banking assistant. How can I help you with your banking needs today?", "timestamp": datetime.now().strftime("%H:%M")}
        ]
        st.session_state.current_chat = chat_name
        st.rerun()
    
    st.markdown("---")
    
    # Chat list
    st.markdown("### Chats")
    for chat_name in st.session_state.chats.keys():
        if st.button(chat_name, key=f"chat_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()
    
    st.markdown("---")
    
    # Banking Services
    st.markdown("### Banking Services")
    st.markdown("""
    - **Balance Inquiry** 
    - **Money Transfer** 
    - **Add Beneficiaries** 
    - **Remove Beneficiaries** 
    - **List Beneficiaries** 
    - **Transaction History**
    """)

# Main content - simple approach
st.markdown("### Welcome to Plutus Banking Assistant")

# Welcome message
if (st.session_state.current_chat and 
    st.session_state.chats[st.session_state.current_chat] and
    len([msg for msg in st.session_state.chats[st.session_state.current_chat] if msg["role"] != "welcome"]) == 0):
    
    st.info("Hello! I'm Plutus, your AI-powered banking assistant. How can I help you with your banking needs today?")

# Chat messages
current_chat_messages = st.session_state.chats[st.session_state.current_chat]
messages_to_show = [msg for msg in current_chat_messages if msg["role"] != "welcome"]

for message in messages_to_show:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']} *({message['timestamp']})*")
    elif message["role"] == "bot":
        st.markdown(f"**Plutus:** {message['content']} *({message['timestamp']})*")

# Input area - simple form
st.markdown("---")
st.markdown("### Send a Message")

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message:",
            placeholder="Ask anything about banking...",
            disabled=st.session_state.is_processing,
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.form_submit_button(
            "Send" if not st.session_state.is_processing else "Processing...",
            disabled=st.session_state.is_processing,
            use_container_width=True
        )

# Handle message sending
if send_button and user_input.strip() and not st.session_state.is_processing:
    st.session_state.is_processing = True
    
    # Add user message
    user_message = {
        "role": "user",
        "content": user_input.strip(),
        "timestamp": datetime.now().strftime("%H:%M")
    }
    st.session_state.chats[st.session_state.current_chat].append(user_message)
    
    # Mock bot response
    bot_response = "I understand you're looking for banking assistance. Could you please clarify what you'd like me to help you with? I can check balances, transfer money, add beneficiaries, or provide statements."
    
    # Add bot response
    bot_message = {
        "role": "bot",
        "content": bot_response,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    st.session_state.chats[st.session_state.current_chat].append(bot_message)
    
    st.session_state.is_processing = False
    st.rerun()
