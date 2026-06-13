from sqlalchemy.ext.asyncio import AsyncSession
from app.core.supabase import get_supabase
from app.core.exceptions import (
    UnauthorizedException,
    ValidationException,
    NotFoundException,
)
from app.models.user import UserRole
from app.schemas.user import (
    SendOtpRequest,
    VerifyOtpRequest,
    LoginRequest,
    TokenResponse,
)
import structlog
import httpx

logger = structlog.get_logger()


def _fetch_user_from_supabase_rest(user_id: str) -> dict | None:
    """
    Fetch user row from public.users via Supabase PostgREST (HTTPS port 443).
    Avoids asyncpg TCP/5432 which fails DNS on Windows.
    """
    from app.core.config import settings

    url = f"{settings.supabase_url}/rest/v1/users"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
    }
    params = {
        "id": f"eq.{user_id}",
        "select": "id,email,full_name,role,is_active,preferred_lang,district,state,phone,created_at",
        "limit": "1",
    }

    try:
        response = httpx.get(
            url,
            headers=headers,
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        if rows:
            logger.info("User fetched from REST", user_id=user_id, role=rows[0].get("role"))
        return rows[0] if rows else None
    except httpx.HTTPError as e:
        logger.error("Supabase REST user fetch failed", error=str(e))
        return None


def _insert_user_to_supabase_rest(user_data: dict) -> dict | None:
    """
    Insert new user row into public.users via Supabase PostgREST.
    Fallback when the auth trigger didn't fire.
    """
    from app.core.config import settings

    url = f"{settings.supabase_url}/rest/v1/users"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    try:
        response = httpx.post(
            url,
            headers=headers,
            json=user_data,
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        return rows[0] if rows else None
    except httpx.HTTPError as e:
        logger.error("Supabase REST user insert failed", error=str(e))
        return None


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.supabase = get_supabase()

    async def send_otp(self, data: SendOtpRequest) -> dict:
        try:
            self.supabase.auth.sign_in_with_otp({
                "email": data.email,
                "options": {
                    "should_create_user": True,
                    "data": {
                        "full_name": data.full_name or data.email.split("@")[0],
                        "role": "farmer",
                        "preferred_lang": data.preferred_lang,
                    },
                },
            })
            logger.info("OTP sent", email=data.email)
            return {"message": "OTP sent to your email", "email": data.email}
        except Exception as e:
            error_str = str(e)
            logger.error("Failed to send OTP", error=error_str, email=data.email)
            raise ValidationException(f"Failed to send OTP: {error_str}")

    async def verify_otp(self, data: VerifyOtpRequest) -> TokenResponse:
        try:
            response = self.supabase.auth.verify_otp({
                "email": data.email,
                "token": data.otp,
                "type": "email",
            })

            session = response.session
            if not session:
                raise UnauthorizedException("Invalid or expired OTP")

            user_id = str(session.user.id)

            db_row = _fetch_user_from_supabase_rest(user_id)

            if not db_row:
                new_row = _insert_user_to_supabase_rest({
                    "id": user_id,
                    "email": data.email,
                    "full_name": session.user.user_metadata.get(
                        "full_name", data.email.split("@")[0]
                    ),
                    "role": "farmer",
                    "preferred_lang": session.user.user_metadata.get(
                        "preferred_lang", "hi"
                    ),
                })
                db_row = new_row

            if not db_row:
                raise UnauthorizedException(
                    "User profile not found. Please contact support."
                )

            logger.info("OTP verified", user_id=user_id)

            from app.schemas.user import UserResponse
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=session.expires_in or 3600,
                user=UserResponse(
                    id=db_row["id"],
                    email=db_row["email"],
                    full_name=db_row["full_name"],
                    phone=db_row.get("phone"),
                    role=UserRole(db_row["role"]),
                    district=db_row.get("district"),
                    state=db_row.get("state", "Uttar Pradesh"),
                    is_active=db_row.get("is_active", True),
                    preferred_lang=db_row.get("preferred_lang", "hi"),
                    created_at=db_row["created_at"],
                ),
            )

        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error("OTP verification failed", error=str(e))
            raise UnauthorizedException("Invalid or expired OTP")

    async def login_with_password(self, data: LoginRequest) -> TokenResponse:
        # Step 1 — Authenticate with Supabase (HTTPS, always works)
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": data.email,
                "password": data.password,
            })
        except Exception as e:
            logger.error("Supabase sign_in failed", error=str(e))
            raise UnauthorizedException("Invalid email or password")

        session = response.session
        if not session:
            raise UnauthorizedException("Invalid email or password")

        user_id = str(session.user.id)
        user_email = session.user.email or data.email
        logger.info("Supabase auth succeeded", user_id=user_id, email=user_email)

        # Step 2 — Fetch profile via REST (HTTPS, no asyncpg/TCP needed)
        db_row = _fetch_user_from_supabase_rest(user_id)

        if not db_row:
            logger.error("User not in public.users", user_id=user_id)
            raise UnauthorizedException(
                "Account profile not found. Contact your administrator."
            )

        # Step 3 — Role check
        role = db_row.get("role", "farmer")

        if role == "farmer":
            raise UnauthorizedException(
                "Farmer accounts must use the FasalSetu mobile app."
            )

        if not db_row.get("is_active", True):
            raise UnauthorizedException("Your account has been deactivated.")

        logger.info("Password login success", user_id=user_id, role=role)

        from app.schemas.user import UserResponse
        return TokenResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user=UserResponse(
                id=db_row["id"],
                email=db_row["email"],
                full_name=db_row["full_name"],
                phone=db_row.get("phone"),
                role=UserRole(role),
                district=db_row.get("district"),
                state=db_row.get("state", "Uttar Pradesh"),
                is_active=db_row.get("is_active", True),
                preferred_lang=db_row.get("preferred_lang", "en"),
                created_at=db_row["created_at"],
            ),
        )

    async def get_me(self, user_id: str) -> dict:
        db_row = _fetch_user_from_supabase_rest(user_id)
        if not db_row:
            raise NotFoundException("User")
        return db_row