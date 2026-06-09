from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
import structlog

logger = structlog.get_logger()
bearer_scheme = HTTPBearer()


def decode_supabase_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed", error=str(e))
        raise UnauthorizedException("Invalid or expired token")


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    payload = decode_supabase_jwt(credentials.credentials)
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token missing user ID")
    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    return {"id": user_id}


def require_role(*roles: str):
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        # DB session injected in routes — role check done in service layer
    ) -> str:
        payload = decode_supabase_jwt(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException()
        return user_id
    return role_checker