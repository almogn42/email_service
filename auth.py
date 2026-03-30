"""
Authentication module for the Email & SMS Service.

Provides three FastAPI dependency functions that can be injected into
route handlers via Depends():
  - verify_basic_auth  — HTTP Basic username/password
  - verify_oauth_token — Bearer token (API key)
  - verify_auth        — accepts either method
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

import base64

# ── Security scheme instances used by FastAPI's OpenAPI docs ───────
security_basic = HTTPBasic()        # Prompts for username/password in Swagger UI
security_bearer = HTTPBearer()      # Prompts for Bearer token in Swagger UI

# ── Password hashing context (PBKDF2-SHA256) ──────────────────────
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its PBKDF2 hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Return the PBKDF2-SHA256 hash of a plain-text password."""
    return pwd_context.hash(password)

# NOTE: This import is intentionally placed here (not at the top of the file)
# to avoid a circular import.  config.py → hash_passwords() → auth.get_password_hash
# runs during Settings initialization, so config must finish loading before
# auth.py tries to import get_settings.
from config import get_settings


# ============================================================================
# Basic Auth Dependency
# ============================================================================

async def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security_basic)) -> str:
    """
    FastAPI dependency — verifies HTTP Basic Auth credentials.

    Returns the authenticated username on success.
    Raises 401 if the username doesn't exist or the password is wrong.
    """
    # get_settings() is cached via @lru_cache — returns the same Settings
    # instance with already-hashed passwords for the entire session
    cached_settings = get_settings()
    
    # Look up the stored hash for the provided username
    stored_hashed_password = cached_settings.BASIC_AUTH_USERS.get(credentials.username)
    
    if stored_hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Compare the plain-text password from the request against the stored hash
    if not verify_password(credentials.password, stored_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username


# ============================================================================
# Bearer Token Dependency
# ============================================================================

async def verify_oauth_token(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)) -> str:
    """
    FastAPI dependency — verifies a Bearer token against the configured API_TOKENS list.

    Returns the token string on success.
    Raises 401 if the token is not in the allowed list.
    """
    settings = get_settings()
    
    if credentials.credentials not in settings.API_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials


# ============================================================================
# Combined Auth Dependency (accepts either method)
# ============================================================================

async def verify_auth(
    basic_credentials: HTTPBasicCredentials = Depends(security_basic),
    bearer_credentials: HTTPAuthorizationCredentials = None
) -> str:
    """
    FastAPI dependency — accepts either Basic Auth or Bearer Token.

    Tries Bearer first (if provided), then falls back to Basic Auth.
    Returns the authenticated username or token string.
    """
    # Try Bearer token first
    if bearer_credentials:
        try:
            return await verify_oauth_token(bearer_credentials)
        except HTTPException:
            pass
    
    # Fall back to Basic Auth
    if basic_credentials:
        return await verify_basic_auth(basic_credentials)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )
