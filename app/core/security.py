"""
Plutus Backend - Security and Authentication Utilities
Handles JWT tokens, password hashing, and security-related functions.

Team: Yay!
Date: August 29, 2025
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
import hashlib
import secrets

from .config import get_settings, Settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class SecurityUtils:
    """
    Security utilities for authentication and data protection.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Generate hash for a password.
        """
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        to_encode.update({"jti": str(uuid.uuid4())})  # JWT ID for token tracking
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.settings.secret_key, 
            algorithm=self.settings.algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        """
        try:
            payload = jwt.decode(
                token, 
                self.settings.secret_key, 
                algorithms=[self.settings.algorithm]
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def validate_account_number(self, account_number: str) -> Dict[str, Any]:
        """
        Validate user-provided account number format.
        Users provide their own account numbers during registration.
        """
        result = {
            "valid": True,
            "errors": [],
            "formatted_number": account_number.replace("-", "").replace(" ", "")
        }
        
        # Remove spaces and hyphens for validation
        clean_number = account_number.replace("-", "").replace(" ", "")
        
        # Check if it's numeric
        if not clean_number.isdigit():
            result["valid"] = False
            result["errors"].append("Account number must contain only digits")
            
        # Check length (typically 10-20 digits for Pakistani banks)
        if len(clean_number) < 10 or len(clean_number) > 20:
            result["valid"] = False
            result["errors"].append("Account number must be between 10-20 digits")
            
        # Check for reasonable patterns (not all same digits)
        if len(set(clean_number)) == 1:
            result["valid"] = False
            result["errors"].append("Account number cannot be all same digits")
            
        return result
    
    def generate_transaction_id(self) -> str:
        """
        Generate unique transaction ID.
        """
        # Generate transaction ID with timestamp and random component
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        return f"TXN{timestamp}{random_part}"
    
    def generate_user_id(self) -> str:
        """
        Generate unique user ID.
        """
        return f"USR{uuid.uuid4().hex[:8].upper()}"
    
    def validate_beneficiary_account(self, account_number: str, bank_name: str) -> Dict[str, Any]:
        """
        Validate beneficiary account details provided by user through chatbot.
        """
        result = {
            "valid": True,
            "errors": []
        }
        
        # Validate account number format
        account_validation = self.validate_account_number(account_number)
        if not account_validation["valid"]:
            result["valid"] = False
            result["errors"].extend(account_validation["errors"])
            
        # Validate bank name
        if not bank_name or len(bank_name.strip()) < 3:
            result["valid"] = False
            result["errors"].append("Bank name must be at least 3 characters")
            
        # List of valid Pakistani banks (can be expanded)
        valid_banks = [
            "HBL", "Habib Bank Limited",
            "UBL", "United Bank Limited", 
            "MCB", "Muslim Commercial Bank",
            "NBP", "National Bank of Pakistan",
            "Allied Bank", "Allied Bank Limited",
            "Standard Chartered", "Standard Chartered Bank",
            "Faysal Bank", "Bank Alfalah",
            "Askari Bank", "JS Bank",
            "Meezan Bank", "Dubai Islamic Bank",
            "Soneri Bank", "Summit Bank",
            "Samba Bank", "KASB Bank"
        ]
        
        # Check if bank name is recognized (case-insensitive partial match)
        bank_found = any(
            bank.lower() in bank_name.lower() or bank_name.lower() in bank.lower() 
            for bank in valid_banks
        )
        
        if not bank_found:
            # Don't reject, but add a warning
            result["warning"] = f"Bank '{bank_name}' not in our common banks list, but proceeding"
            
        return result
    
    def generate_beneficiary_id(self) -> str:
        """
        Generate unique beneficiary ID.
        """
        return f"BEN{uuid.uuid4().hex[:8].upper()}"
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Hash sensitive data for audit logging.
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength and return validation result.
        """
        result = {
            "valid": True,
            "errors": [],
            "score": 0
        }
        
        # Check minimum length
        if len(password) < 8:
            result["valid"] = False
            result["errors"].append("Password must be at least 8 characters long")
        else:
            result["score"] += 1
            
        # Check for uppercase letter
        if not any(c.isupper() for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one uppercase letter")
        else:
            result["score"] += 1
            
        # Check for lowercase letter
        if not any(c.islower() for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one lowercase letter")
        else:
            result["score"] += 1
            
        # Check for digit
        if not any(c.isdigit() for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one digit")
        else:
            result["score"] += 1
            
        # Check for special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one special character")
        else:
            result["score"] += 1
            
        return result


# Global security utils instance
security_utils = SecurityUtils(get_settings())


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token.
    """
    try:
        token = credentials.credentials
        payload = security_utils.verify_token(token)
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "account_number": payload.get("account_number"),
            "token_exp": payload.get("exp"),
            "token_issued": payload.get("iat")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current user if token is provided (optional authentication).
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def create_audit_log_entry(
    user_id: str,
    action: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized audit log entry.
    """
    return {
        "log_id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "details": str(details),  # Convert to string for CSV storage
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": ip_address or "unknown",
        "request_id": request_id or "unknown"
    }


# Password and security validation functions
def get_security_utils() -> SecurityUtils:
    """
    Dependency to get security utils instance.
    """
    return security_utils


def get_security_manager() -> SecurityUtils:
    """
    Dependency to get security manager instance (alias for security utils).
    """
    return security_utils
