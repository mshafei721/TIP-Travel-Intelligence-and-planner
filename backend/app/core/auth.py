"""Authentication utilities for FastAPI"""

import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from jose import ExpiredSignatureError, JWTError, jwt

# JWTClaimsError may not exist in older versions of python-jose
try:
    from jose import JWTClaimsError
except ImportError:
    # Fallback: treat JWTClaimsError as JWTError
    JWTClaimsError = JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_jwt_token(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Verify JWT token from Authorization header.

    Returns decoded token payload with user_id.
    Uses secure error messages that don't leak internal details.

    Args:
        request: FastAPI request object (auto-injected)
        authorization: Bearer token from header

    Returns:
        dict: Decoded token payload containing user_id

    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        logger.warning(
            "Missing authorization header",
            extra={"path": request.url.path}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2:
            raise ValueError("Invalid format")

        scheme, token = parts
        if scheme.lower() != "bearer":
            logger.warning("Invalid authentication scheme used")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode and verify token with explicit options
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_aud": False,  # Supabase doesn't use aud claim
                "verify_exp": True,   # Explicitly verify expiration
                "require": ["sub", "exp"],  # Require these claims
            },
        )

        # Extract and validate user_id
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing required 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Set user_id on request state for rate limiting and logging
        request.state.user_id = user_id

        return {"user_id": user_id, **payload}

    except ValueError:
        logger.warning("Invalid authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        logger.info("Expired token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTClaimsError:
        logger.warning("Invalid JWT claims")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        # Don't log the exception details - could contain sensitive info
        logger.warning("JWT validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def optional_jwt_token(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """
    Optionally verify JWT token from Authorization header.

    Returns decoded token payload if present and valid, otherwise None.
    Does not raise exceptions for missing or invalid tokens.

    Args:
        request: FastAPI request object (auto-injected)
        authorization: Bearer token from header (optional)

    Returns:
        Optional[dict]: Decoded token payload containing user_id, or None
    """
    if not authorization:
        return None

    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2:
            return None

        scheme, token = parts
        if scheme.lower() != "bearer":
            return None

        # Decode and verify token with explicit options
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_aud": False,  # Supabase doesn't use aud claim
                "verify_exp": True,   # Explicitly verify expiration
                "require": ["sub", "exp"],  # Require these claims
            },
        )

        # Extract and validate user_id
        user_id = payload.get("sub")
        if not user_id:
            return None

        # Set user_id on request state for rate limiting and logging
        request.state.user_id = user_id

        return {"user_id": user_id, **payload}

    except (ValueError, ExpiredSignatureError, JWTClaimsError, JWTError):
        # Return None for any token validation failures
        return None
