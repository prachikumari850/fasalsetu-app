# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import jwt, JWTError
# from app.core.config import settings
# from app.core.exceptions import UnauthorizedException
# import structlog

# logger = structlog.get_logger()
# bearer_scheme = HTTPBearer()


# def decode_supabase_jwt(token: str) -> dict:
#     try:
#         payload = jwt.decode(
#             token,
#             settings.supabase_jwt_secret,
#             algorithms=["HS256"],
#             options={"verify_aud": False},
#         )
#         return payload
#     except JWTError as e:
#         logger.warning("JWT decode failed", error=str(e))
#         raise UnauthorizedException("Invalid or expired token")


# async def get_current_user_id(
#     credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
# ) -> str:
#     payload = decode_supabase_jwt(credentials.credentials)
#     user_id: str = payload.get("sub")
#     if not user_id:
#         raise UnauthorizedException("Token missing user ID")
#     return user_id


# async def get_current_user(
#     user_id: str = Depends(get_current_user_id),
# ) -> dict:
#     return {"id": user_id}


# def require_role(*roles: str):
#     async def role_checker(
#         credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
#         # DB session injected in routes — role check done in service layer
#     ) -> str:
#         payload = decode_supabase_jwt(credentials.credentials)
#         user_id = payload.get("sub")
#         if not user_id:
#             raise UnauthorizedException()
#         return user_id
#     return role_checker

from __future__ import annotations
import time
import httpx
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
import structlog

logger = structlog.get_logger()
bearer_scheme = HTTPBearer()

# ── JWKS cache ────────────────────────────────────────────────────────────────
# Keys are fetched once and cached for 1 hour (Supabase rotates ~daily)
_JWKS_CACHE: dict = {}
_JWKS_FETCHED_AT: float = 0.0
_JWKS_TTL_SECONDS = 3600


def _fetch_jwks() -> dict:
    """Fetch JWKS from Supabase and cache it."""
    global _JWKS_CACHE, _JWKS_FETCHED_AT

    now = time.monotonic()
    if _JWKS_CACHE and (now - _JWKS_FETCHED_AT) < _JWKS_TTL_SECONDS:
        return _JWKS_CACHE

    url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    try:
        resp = httpx.get(url, timeout=10.0, headers={
            "apikey": settings.supabase_anon_key,
        })
        resp.raise_for_status()
        _JWKS_CACHE      = resp.json()
        _JWKS_FETCHED_AT = now
        logger.info("JWKS refreshed", key_count=len(_JWKS_CACHE.get("keys", [])))
        return _JWKS_CACHE
    except Exception as e:
        logger.error("JWKS fetch failed", error=str(e))
        if _JWKS_CACHE:
            logger.warning("Using stale JWKS cache")
            return _JWKS_CACHE
        raise UnauthorizedException("Cannot validate token: JWKS unavailable")


def _verify_token_via_jwks(token: str) -> dict:
    """
    Verify a Supabase JWT using JWKS (ES256).
    Returns the decoded payload if valid.
    """
    import jwt as pyjwt
    from jwt import PyJWKClient, PyJWKClientError

    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"

    try:
        # PyJWT's PyJWKClient handles kid lookup, key conversion, and caching
        jwks_client = PyJWKClient(
            jwks_url,
            headers={"apikey": settings.supabase_anon_key},
            cache_keys=True,
            lifespan=_JWKS_TTL_SECONDS,
        )
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],    # accept both; Supabase uses ES256
            options={"verify_aud": False},     # Supabase aud=authenticated, not a URL
        )
        return payload

    except PyJWKClientError as e:
        logger.warning("JWKS key lookup failed", error=str(e))
        raise UnauthorizedException("Token key not found in JWKS")
    except pyjwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except pyjwt.InvalidTokenError as e:
        logger.warning("JWT validation failed", error=str(e))
        raise UnauthorizedException("Invalid token")


def _verify_token_via_introspection(token: str) -> dict:
    """
    Fallback: verify token by calling Supabase GET /auth/v1/user.
    Less efficient (1 HTTP call per request) but works without JWKS.
    """
    url = f"{settings.supabase_url}/auth/v1/user"
    try:
        resp = httpx.get(
            url,
            headers={
                "apikey":        settings.supabase_anon_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )
        if resp.status_code == 200:
            user_data = resp.json()
            return {
                "sub":   user_data.get("id"),
                "email": user_data.get("email"),
                "role":  user_data.get("role", "authenticated"),
            }
        raise UnauthorizedException("Invalid or expired token")
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.error("Token introspection failed", error=str(e))
        raise UnauthorizedException("Cannot validate token")


def decode_supabase_jwt(token: str) -> dict:
    """
    Validate a Supabase JWT.
    Primary:  JWKS-based ES256 verification (cryptographically correct)
    Fallback: Token introspection via Supabase REST API
    """
    try:
        return _verify_token_via_jwks(token)
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.warning(
            "JWKS verification failed, trying introspection",
            error=str(e),
        )
        return _verify_token_via_introspection(token)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    payload = decode_supabase_jwt(credentials.credentials)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token missing user ID")
    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    return {"id": user_id}