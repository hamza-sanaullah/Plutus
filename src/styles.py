# CSS styles for Plutus Banking Assistant

def get_light_theme_css():
    """Get light theme CSS styles"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Main app styling */
        .main {
            background: #ffffff;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
            min-height: 100vh;
            padding: 0;
        }
        
        /* Overall page background */
        .stApp {
            background: #ffffff;
        }
        
        /* Main content container */
        .main .block-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 0;
        }
        
        /* Ensure main content is visible */
        .main {
            margin-left: 0;
        }
        
        /* Hide Streamlit's default elements */
        .stApp > header {
            display: none;
        }
        
        .stApp > div:first-child {
            display: none;
        }
        
        /* Sidebar styling */
        .sidebar .block-container {
            background: #f7f7f8;
            border: none;
            border-radius: 0;
            margin: 0;
            padding: 0;
            box-shadow: none;
        }
        
        /* Header styling */
        .header-container {
            text-align: center;
            padding: 2rem 0 1rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .main-title {
            color: #1a1a1a;
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
        }
        
        .subtitle {
            color: #6c757d;
            font-size: 1rem;
            margin-top: 0.5rem;
            font-weight: 400;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar specific styling */
        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .sidebar-title {
            color: #1a1a1a;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
            font-size: 1.2rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .sidebar-toggle {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 4px;
            color: #666;
            font-size: 1.2rem;
        }
        
        .sidebar-toggle:hover {
            background: #f0f0f0;
        }
        
        /* Override Streamlit button styles */
        .stButton > button {
            background: transparent !important;
            color: #1a1a1a !important;
            border: 1px solid #e5e5e5 !important;
            border-radius: 6px !important;
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0 !important;
            font-weight: 400 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol" !important;
            font-size: 14px !important;
            line-height: 20px !important;
            text-align: left !important;
            width: 100% !important;
            box-shadow: none !important;
        }
        
        .stButton > button:hover {
            background: #f0f0f0 !important;
            border-color: #d0d0d0 !important;
            transform: none !important;
        }
        
        .stButton > button:focus {
            box-shadow: none !important;
        }
        
        .chat-list {
            padding: 0 1rem;
        }
        
        .service-dropdown {
            margin: 1rem;
        }
        
        /* Chat area styling */
        .chat-container {
            height: 100vh;
            overflow-y: auto;
            padding: 0;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        
        .welcome-message {
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
            margin: 0 0 3rem 0;
            max-width: 600px;
            text-align: center;
            color: #1a1a1a;
            font-size: 1.5rem;
            line-height: 1.4;
            font-weight: 400;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
        }
        
        .chat-messages {
            flex: 1;
            width: 100%;
            max-width: 800px;
            padding: 1rem;
            overflow-y: auto;
            margin-bottom: 120px;
        }
        
        .message-container {
            margin: 1rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .user-message-container {
            justify-content: flex-end;
            flex-direction: row-reverse;
        }
        
        .bot-message-container {
            justify-content: flex-start;
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            flex-shrink: 0;
            margin-top: 5px;
        }
        
        .user-avatar {
            background: #007bff;
            color: white;
        }
        
        .bot-avatar {
            background: #6c757d;
            color: white;
        }
        
        .message-bubble {
            max-width: 70%;
            padding: 1rem 1.25rem;
            border-radius: 18px;
            word-wrap: break-word;
            font-family: 'Inter', sans-serif;
            line-height: 1.5;
        }
        
        .user-message {
            background: #007bff;
            color: white;
        }
        
        .bot-message {
            background: #f8f9fa;
            color: #1a1a1a;
            border: 1px solid #e9ecef;
        }
        
        .timestamp {
            font-size: 0.75rem;
            color: #6c757d;
            margin-top: 0.5rem;
            text-align: right;
        }
        
        /* Input area styling */
        .input-container {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: transparent;
            border: none;
            padding: 0;
            z-index: 1000;
            width: 100%;
            max-width: 800px;
        }
        
        .input-row {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 24px;
            padding: 0.75rem 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        
        .input-row:focus-within {
            border-color: #007bff;
            box-shadow: 0 4px 12px rgba(0,123,255,0.2);
        }
        
        .stTextInput input {
            border: none;
            border-radius: 0;
            padding: 0.5rem 0.75rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
            background: transparent;
            color: #1a1a1a;
        }
        
        .stTextInput input:focus {
            border: none;
            box-shadow: none;
            outline: none;
        }
        
        .stTextInput input::placeholder {
            color: #9ca3af;
        }
        
        .stButton button {
            background: #007bff !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol" !important;
            min-width: 60px !important;
        }
        
        .stButton button:hover {
            background: #0056b3 !important;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 1001;
            background: #ffffff;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            padding: 0.5rem;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 1.2rem;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        /* JavaScript for sidebar toggle */
        <script>
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.style.display = sidebar.style.display === 'none' ? 'block' : 'none';
            }
        }
        </script>
    </style>
    """

def get_dark_theme_css():
    """Get dark theme CSS styles"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Main app styling */
        .main {
            background: #212121;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
            min-height: 100vh;
            padding: 0;
        }
        
        /* Overall page background */
        .stApp {
            background: #212121;
        }
        
        /* Main content container */
        .main .block-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 0;
        }
        
        /* Ensure main content is visible */
        .main {
            margin-left: 0;
        }
        
        /* Hide Streamlit's default elements */
        .stApp > header {
            display: none;
        }
        
        .stApp > div:first-child {
            display: none;
        }
        
        /* Sidebar styling */
        .sidebar .block-container {
            background: #171717;
            border: none;
            border-radius: 0;
            margin: 0;
            padding: 0;
            box-shadow: none;
        }
        
        /* Header styling */
        .header-container {
            text-align: center;
            padding: 2rem 0 1rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid #404040;
        }
        
        .main-title {
            color: #ffffff;
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
        }
        
        .subtitle {
            color: #b0b0b0;
            font-size: 1rem;
            margin-top: 0.5rem;
            font-weight: 400;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar specific styling */
        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            border-bottom: 1px solid #404040;
        }
        
        .sidebar-title {
            color: #ffffff;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
            font-size: 1.2rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .sidebar-toggle {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 4px;
            color: #afafaf;
            font-size: 1.2rem;
        }
        
        .sidebar-toggle:hover {
            background: #404040;
        }
        
        /* Override Streamlit button styles for dark theme */
        .stButton > button {
            background: transparent !important;
            color: #afafaf !important;
            border: 1px solid #404040 !important;
            border-radius: 6px !important;
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0 !important;
            font-weight: 400 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol" !important;
            font-size: 14px !important;
            line-height: 20px !important;
            text-align: left !important;
            width: 100% !important;
            box-shadow: none !important;
        }
        
        .stButton > button:hover {
            background: #404040 !important;
            border-color: #555555 !important;
            transform: none !important;
        }
        
        .stButton > button:focus {
            box-shadow: none !important;
        }
        
        .chat-list {
            padding: 0 1rem;
        }
        
        .service-dropdown {
            margin: 1rem;
        }
        
        /* Chat area styling */
        .chat-container {
            height: 100vh;
            overflow-y: auto;
            padding: 0;
            background: #212121;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        
        .welcome-message {
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
            margin: 0 0 3rem 0;
            max-width: 600px;
            text-align: center;
            color: #ffffff;
            font-size: 1.5rem;
            line-height: 1.4;
            font-weight: 400;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
        }
        
        .chat-messages {
            flex: 1;
            width: 100%;
            max-width: 800px;
            padding: 1rem;
            overflow-y: auto;
            margin-bottom: 120px;
        }
        
        .message-container {
            margin: 1rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .user-message-container {
            justify-content: flex-end;
            flex-direction: row-reverse;
        }
        
        .bot-message-container {
            justify-content: flex-start;
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            flex-shrink: 0;
            margin-top: 5px;
        }
        
        .user-avatar {
            background: #007bff;
            color: white;
        }
        
        .bot-avatar {
            background: #6c757d;
            color: white;
        }
        
        .message-bubble {
            max-width: 70%;
            padding: 1rem 1.25rem;
            border-radius: 18px;
            word-wrap: break-word;
            font-family: 'Inter', sans-serif;
            line-height: 1.5;
        }
        
        .user-message {
            background: #007bff;
            color: white;
        }
        
        .bot-message {
            background: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #404040;
        }
        
        .timestamp {
            font-size: 0.75rem;
            color: #b0b0b0;
            margin-top: 0.5rem;
            text-align: right;
        }
        
        /* Input area styling */
        .input-container {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: transparent;
            border: none;
            padding: 0;
            z-index: 1000;
            width: 100%;
            max-width: 800px;
        }
        
        .input-row {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            background: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 24px;
            padding: 0.75rem 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        
        .input-row:focus-within {
            border-color: #007bff;
            box-shadow: 0 4px 12px rgba(0,123,255,0.2);
        }
        
        .stTextInput input {
            border: none;
            border-radius: 0;
            padding: 0.5rem 0.75rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
            background: transparent;
            color: #ffffff;
        }
        
        .stTextInput input:focus {
            border: none;
            box-shadow: none;
            outline: none;
        }
        
        .stTextInput input::placeholder {
            color: #9ca3af;
        }
        
        .stButton button {
            background: #007bff !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol" !important;
            min-width: 60px !important;
        }
        
        .stButton button:hover {
            background: #0056b3 !important;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 1001;
            background: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 0.5rem;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-size: 1.2rem;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #2d2d2d;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #555555;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #777777;
        }
        
        /* JavaScript for sidebar toggle */
        <script>
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.style.display = sidebar.style.display === 'none' ? 'block' : 'none';
            }
        }
        </script>
    </style>
    """
