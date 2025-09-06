# UI Components for Plutus Banking Assistant

import streamlit as st
from config import BANKING_SERVICES
from utils import get_current_placeholder, format_timestamp

def render_sidebar():
    """Render the sidebar with chat management and banking services"""
    with st.sidebar:
        st.markdown("## 🏦 Plutus")
        
        # New Chat Button
        if st.button("+ New Chat", key="new_chat", use_container_width=True):
            from utils import create_new_chat
            create_new_chat()
            st.rerun()
        
        st.markdown("---")
        
        # Chat list
        st.markdown("### Chats")
        if st.session_state.chats:
            for chat_name in st.session_state.chats.keys():
                if st.button(chat_name, key=f"chat_{chat_name}", use_container_width=True):
                    st.session_state.current_chat = chat_name
                    st.rerun()
        
        st.markdown("---")
        
        # Banking Services Dropdown
        st.markdown("### Banking Services")
        
        # Service selection
        selected_service = st.selectbox(
            "Select a service:",
            options=[""] + list(BANKING_SERVICES.keys()),
            format_func=lambda x: BANKING_SERVICES[x]["name"] if x else "Choose a service...",
            key="service_selector"
        )
        
        if selected_service:
            st.session_state.selected_service = selected_service
            st.info(f"💡 {BANKING_SERVICES[selected_service]['description']}")

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="header-container">
        <div class="main-title">Plutus</div>
        <div class="subtitle">Your AI-Powered Banking Assistant</div>
    </div>
    """, unsafe_allow_html=True)

def render_theme_toggle():
    """Render the theme toggle button"""
    theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
    
    if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

def render_welcome_message():
    """Render the welcome message"""
    if st.session_state.current_chat and st.session_state.chats[st.session_state.current_chat]:
        welcome_msg = st.session_state.chats[st.session_state.current_chat][0]
        if welcome_msg["role"] == "welcome":
            st.markdown(f"""
            <div class="welcome-message">
                Hello! I'm Plutus, your AI-powered banking assistant. How can I help you with your banking needs today?
            </div>
            """, unsafe_allow_html=True)

def render_chat_messages():
    """Render chat messages"""
    if not st.session_state.current_chat or st.session_state.current_chat not in st.session_state.chats:
        return
    
    current_chat_messages = st.session_state.chats[st.session_state.current_chat]
    
    # Skip the welcome message as it's rendered separately
    messages_to_show = [msg for msg in current_chat_messages if msg["role"] != "welcome"]
    
    if messages_to_show:
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        for message in messages_to_show:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-container user-message-container">
                    <div class="avatar user-avatar">U</div>
                    <div class="message-bubble user-message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif message["role"] == "bot":
                st.markdown(f"""
                <div class="message-container bot-message-container">
                    <div class="avatar bot-avatar">P</div>
                    <div class="message-bubble bot-message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_input_area():
    """Render the input area"""
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            placeholder_text = get_current_placeholder()
            user_input = st.text_input(
                "",
                placeholder=placeholder_text,
                disabled=st.session_state.is_processing,
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button(
                "Send" if not st.session_state.is_processing else "Processing...",
                disabled=st.session_state.is_processing,
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return user_input, send_button
