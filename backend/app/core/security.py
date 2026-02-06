"""
Security utilities for authentication, authorization, and encryption.
Provides JWT token management, password hashing, and API key validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import hashlib
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Centralized security management for the application."""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.debug(f"Access token created for: {data.get('sub', 'unknown')}")
        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=self.refresh_token_expire_days
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.debug(f"Refresh token created for: {data.get('sub', 'unknown')}")
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token decode failed: {e}")
            return None

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and check its type.

        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")

        Returns:
            Decoded token payload or None if invalid
        """
        payload = self.decode_token(token)

        if not payload:
            return None

        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token has expired")
            return None

        return payload

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_api_key(prefix: str = "sk") -> str:
        """
        Generate a secure API key.

        Args:
            prefix: Prefix for the API key

        Returns:
            Generated API key string
        """
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key for storage.

        Args:
            api_key: API key to hash

        Returns:
            SHA-256 hash of the API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def verify_api_key(plain_key: str, hashed_key: str) -> bool:
        """
        Verify an API key against its hash.

        Args:
            plain_key: Plain text API key
            hashed_key: Hashed API key to compare against

        Returns:
            True if API key matches, False otherwise
        """
        return SecurityManager.hash_api_key(plain_key) == hashed_key

    @staticmethod
    def generate_random_token(length: int = 32) -> str:
        """
        Generate a random secure token.

        Args:
            length: Length of the token in bytes

        Returns:
            URL-safe random token string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def constant_time_compare(val1: str, val2: str) -> bool:
        """
        Constant time string comparison to prevent timing attacks.

        Args:
            val1: First string
            val2: Second string

        Returns:
            True if strings match, False otherwise
        """
        return secrets.compare_digest(val1, val2)


# Global security manager instance
security_manager = SecurityManager()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token (convenience function).

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    return security_manager.create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token (convenience function).

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    return security_manager.create_refresh_token(data, expires_delta)


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify JWT token (convenience function).

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload or None if invalid
    """
    return security_manager.verify_token(token, token_type)


def hash_password(password: str) -> str:
    """
    Hash a password (convenience function).

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return security_manager.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password (convenience function).

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return security_manager.verify_password(plain_password, hashed_password)


def generate_api_key(prefix: str = "sk") -> str:
    """
    Generate a secure API key (convenience function).

    Args:
        prefix: Prefix for the API key

    Returns:
        Generated API key string
    """
    return security_manager.generate_api_key(prefix)
