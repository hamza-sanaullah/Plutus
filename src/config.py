# Configuration file for Plutus Banking Assistant

# API Configuration
API_URL = "https://plutus-agents-fastapi.thankfuldune-44f528ab.eastus2.azurecontainerapps.io/chat_v1"
API_TIMEOUT = 100

# Banking Services Configuration
BANKING_SERVICES = {
    "balance_inquiry": {
        "name": "Balance Inquiry",
        "placeholder": "Check my account balance",
        "description": "View your current account and savings balance"
    },
    "money_transfer": {
        "name": "Money Transfer", 
        "placeholder": "Send $100 to John Doe",
        "description": "Transfer money to another account"
    },
    "add_beneficiary": {
        "name": "Add Beneficiaries",
        "placeholder": "Add John Doe as beneficiary",
        "description": "Add a new beneficiary to your account"
    },
    "remove_beneficiary": {
        "name": "Remove Beneficiaries",
        "placeholder": "Remove John Doe from beneficiaries",
        "description": "Remove a beneficiary from your account"
    },
    "list_beneficiaries": {
        "name": "List Beneficiaries",
        "placeholder": "Show my beneficiaries",
        "description": "View all your beneficiaries"
    },
    "transaction_history": {
        "name": "Transaction History",
        "placeholder": "Show my recent transactions",
        "description": "View your transaction history"
    }
}

# Welcome Messages
WELCOME_MESSAGES = [
    "Welcome to Plutus! I'm your intelligent banking assistant, here to make your financial management seamless and secure. Whether you need to check balances, transfer funds, or get account insights, I'm ready to help you 24/7.",
    "Hello! I'm Plutus, your AI-powered banking companion. I can help you with account balances, money transfers, beneficiary management, and much more. What would you like to do today?",
    "Hi there! Welcome to Plutus Banking Assistant. I'm here to simplify your banking experience with secure, intelligent assistance. How can I help you manage your finances today?",
    "Greetings! I'm Plutus, your trusted banking AI. From checking balances to processing transfers, I'm equipped to handle all your banking needs efficiently and securely.",
    "Welcome! I'm Plutus, your personal banking assistant. Whether you need to check your balance, send money, or manage beneficiaries, I'm here to make banking effortless for you."
]

# App Configuration
APP_CONFIG = {
    "page_title": "Plutus - AI Banking Assistant",
    "page_icon": "🏦",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
