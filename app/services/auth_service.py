"""
Plutus Backend - Authentication Service
Handles user registration, login, token validation, and authentication logic.

Team: Yay!
Date: August 29, 2025
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from .base_service import BaseService
from ..schemas.auth_schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    PasswordChangeRequest
)


class AuthService(BaseService):
    """
    Authentication service for user management and security operations.
    """
    
    async def register_user(
        self,
        registration_data: UserRegistrationRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with validation and security checks.
        """
        try:
            # Check if username already exists
            existing_user = await self.get_user_by_username(registration_data.username)
            if existing_user:
                await self.log_audit(
                    user_id="system",
                    action="registration_failed",
                    details={
                        "username": registration_data.username,
                        "reason": "Username already exists"
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                return self.create_error_response(
                    "Username already exists",
                    "USERNAME_EXISTS"
                )
            
            # Check if account number already exists
            existing_account = await self.get_user_by_account_number(registration_data.account_number)
            if existing_account:
                await self.log_audit(
                    user_id="system",
                    action="registration_failed",
                    details={
                        "username": registration_data.username,
                        "account_number": registration_data.account_number,
                        "reason": "Account number already exists"
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                return self.create_error_response(
                    "Account number already registered",
                    "ACCOUNT_EXISTS"
                )
            
            # Validate account number format
            account_validation = self.security.validate_account_number(registration_data.account_number)
            if not account_validation["valid"]:
                return self.create_error_response(
                    f"Invalid account number: {', '.join(account_validation['errors'])}",
                    "INVALID_ACCOUNT"
                )
            
            # Generate user ID and hash password
            user_id = self.security.generate_user_id()
            hashed_password = self.security.get_password_hash(registration_data.password)
            
            # Create user data
            user_data = {
                "user_id": user_id,
                "username": registration_data.username.lower(),
                "hashed_password": hashed_password,
                "account_number": account_validation["formatted_number"],
                "balance": registration_data.initial_balance,
                "daily_limit": registration_data.daily_limit,
                "created_at": self.create_timestamp()
            }
            
            # Save user to CSV
            success = await self.storage.append_csv(self.settings.users_csv, user_data)
            
            if not success:
                return self.create_error_response(
                    "Failed to create user account",
                    "REGISTRATION_FAILED"
                )
            
            # Log successful registration
            await self.log_audit(
                user_id=user_id,
                action="user_registered",
                details={
                    "username": registration_data.username,
                    "account_number": account_validation["formatted_number"],
                    "initial_balance": registration_data.initial_balance,
                    "daily_limit": registration_data.daily_limit
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"User registered successfully: {registration_data.username} ({user_id})")
            
            # Return success response (without sensitive data)
            return self.create_success_response(
                "User registered successfully",
                {
                    "user_id": user_id,
                    "username": registration_data.username,
                    "account_number": account_validation["formatted_number"],
                    "balance": registration_data.initial_balance,
                    "daily_limit": registration_data.daily_limit,
                    "created_at": user_data["created_at"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Registration failed for {registration_data.username}: {str(e)}")
            return self.create_error_response(
                "Registration failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def login_user(
        self,
        login_data: UserLoginRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user and generate access token.
        """
        try:
            # Get user by username
            user = await self.get_user_by_username(login_data.username)
            
            if not user:
                await self.log_audit(
                    user_id="system",
                    action="login_failed",
                    details={
                        "username": login_data.username,
                        "reason": "User not found"
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                return self.create_error_response(
                    "Invalid username or password",
                    "INVALID_CREDENTIALS"
                )
            
            # Verify password
            if not self.security.verify_password(login_data.password, user['hashed_password']):
                await self.log_audit(
                    user_id=user['user_id'],
                    action="login_failed",
                    details={
                        "username": login_data.username,
                        "reason": "Invalid password"
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                return self.create_error_response(
                    "Invalid username or password",
                    "INVALID_CREDENTIALS"
                )
            
            # Generate access token
            token_data = {
                "sub": user['user_id'],
                "username": user['username'],
                "account_number": user['account_number']
            }
            
            access_token = self.security.create_access_token(token_data)
            
            # Log successful login
            await self.log_audit(
                user_id=user['user_id'],
                action="login_success",
                details={
                    "username": login_data.username
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"User logged in successfully: {login_data.username}")
            
            return self.create_success_response(
                "Login successful",
                {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": self.settings.access_token_expire_minutes * 60,
                    "user_info": {
                        "user_id": user['user_id'],
                        "username": user['username'],
                        "account_number": user['account_number']
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Login failed for {login_data.username}: {str(e)}")
            return self.create_error_response(
                "Login failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and return user information.
        """
        try:
            # Verify token
            payload = self.security.verify_token(token)
            
            user_id = payload.get("sub")
            if not user_id:
                return self.create_error_response(
                    "Invalid token: missing user ID",
                    "INVALID_TOKEN"
                )
            
            # Get current user data
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "Token valid but user not found",
                    "USER_NOT_FOUND"
                )
            
            return self.create_success_response(
                "Token is valid",
                {
                    "user_id": user['user_id'],
                    "username": user['username'],
                    "account_number": user['account_number'],
                    "token_expires_at": datetime.fromtimestamp(payload.get("exp")).isoformat() + "Z"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Token validation failed: {str(e)}")
            return self.create_error_response(
                "Invalid or expired token",
                "INVALID_TOKEN"
            )
    
    async def change_password(
        self,
        user_id: str,
        password_data: PasswordChangeRequest,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change user password with validation.
        """
        try:
            # Get user
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            # Verify current password
            if not self.security.verify_password(password_data.current_password, user['hashed_password']):
                await self.log_audit(
                    user_id=user_id,
                    action="password_change_failed",
                    details={
                        "reason": "Invalid current password"
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                return self.create_error_response(
                    "Current password is incorrect",
                    "INVALID_PASSWORD"
                )
            
            # Hash new password
            new_hashed_password = self.security.get_password_hash(password_data.new_password)
            
            # Update password in CSV
            success = await self.storage.update_row(
                self.settings.users_csv,
                {"user_id": user_id},
                {"hashed_password": new_hashed_password}
            )
            
            if not success:
                return self.create_error_response(
                    "Failed to update password",
                    "UPDATE_FAILED"
                )
            
            # Log password change
            await self.log_audit(
                user_id=user_id,
                action="password_changed",
                details={
                    "username": user['username']
                },
                ip_address=ip_address,
                request_id=request_id
            )
            
            self.logger.info(f"Password changed for user: {user['username']}")
            
            return self.create_success_response("Password changed successfully")
            
        except Exception as e:
            self.logger.error(f"Password change failed for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Password change failed due to internal error",
                "INTERNAL_ERROR"
            )
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information.
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return self.create_error_response(
                    "User not found",
                    "USER_NOT_FOUND"
                )
            
            # Get last login from audit logs
            audit_df = await self.storage.read_csv(self.settings.audit_logs_csv)
            last_login = None
            
            if not audit_df.empty:
                login_logs = audit_df[
                    (audit_df['user_id'] == user_id) &
                    (audit_df['action'] == 'login_success')
                ].sort_values('timestamp', ascending=False)
                
                if not login_logs.empty:
                    last_login = login_logs.iloc[0]['timestamp']
            
            return self.create_success_response(
                "User profile retrieved",
                {
                    "user_id": user['user_id'],
                    "username": user['username'],
                    "account_number": user['account_number'],
                    "balance": float(user['balance']),
                    "daily_limit": float(user['daily_limit']),
                    "created_at": user['created_at'],
                    "last_login": last_login
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get profile for user {user_id}: {str(e)}")
            return self.create_error_response(
                "Failed to retrieve user profile",
                "INTERNAL_ERROR"
            )
    
    async def logout_user(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log user logout (for audit purposes).
        """
        try:
            user = await self.get_user_by_id(user_id)
            if user:
                await self.log_audit(
                    user_id=user_id,
                    action="logout",
                    details={
                        "username": user['username']
                    },
                    ip_address=ip_address,
                    request_id=request_id
                )
                
                self.logger.info(f"User logged out: {user['username']}")
            
            return self.create_success_response("Logged out successfully")
            
        except Exception as e:
            self.logger.error(f"Logout failed for user {user_id}: {str(e)}")
            return self.create_success_response("Logged out successfully")  # Always succeed logout


# Global instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """
    Dependency to get authentication service instance.
    """
    return auth_service
