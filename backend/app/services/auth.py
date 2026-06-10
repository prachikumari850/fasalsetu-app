from sqlalchemy.ext.asyncio import AsyncSession
from app.core.supabase import get_supabase
from app.core.exceptions import (
    UnauthorizedException,
    ValidationException,
    NotFoundException,
)
from app.repositories.user import UserRepository
from app.models.user import User, UserRole
from app.schemas.user import SendOtpRequest, VerifyOtpRequest, LoginRequest, TokenResponse
import structlog

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.supabase = get_supabase()

    async def send_otp(self, data: SendOtpRequest) -> dict:
        """Send magic link / OTP email via Supabase Auth."""
        try:
            response = self.supabase.auth.sign_in_with_otp({
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
            logger.error("Failed to send OTP", error=str(e), email=data.email)
            raise ValidationException(f"Failed to send OTP: {str(e)}")

    async def verify_otp(self, data: VerifyOtpRequest) -> TokenResponse:
        """Verify OTP and return JWT tokens."""
        try:
            response = self.supabase.auth.verify_otp({
                "email": data.email,
                "token": data.otp,
                "type": "email",
            })

            if not response.session:
                raise UnauthorizedException("Invalid or expired OTP")

            session = response.session
            user_id = session.user.id

            # Ensure profile exists in public.users
            try:
                db_user = await self.user_repo.get_by_id(user_id)
            except NotFoundException:
                # Trigger didn't fire or race condition — create manually
                db_user = User(
                    id=user_id,
                    email=data.email,
                    full_name=session.user.user_metadata.get("full_name", data.email.split("@")[0]),
                    role=UserRole.farmer,
                    preferred_lang=session.user.user_metadata.get("preferred_lang", "hi"),
                )
                self.db.add(db_user)
                await self.db.flush()
                await self.db.refresh(db_user)

            logger.info("OTP verified", user_id=str(user_id), email=data.email)

            from app.schemas.user import UserResponse
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=session.expires_in or 3600,
                user=UserResponse.model_validate(db_user),
            )

        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error("OTP verification failed", error=str(e))
            raise UnauthorizedException("Invalid or expired OTP")

    async def login_with_password(self, data: LoginRequest) -> TokenResponse:
        """Email + password login for officers and admins."""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": data.email,
                "password": data.password,
            })

            if not response.session:
                raise UnauthorizedException("Invalid email or password")

            session = response.session
            user_id = session.user.id

            try:
                db_user = await self.user_repo.get_by_id(user_id)
            except NotFoundException:
                raise UnauthorizedException("Account not found. Contact your administrator.")

            if db_user.role == UserRole.farmer:
                raise UnauthorizedException(
                    "Farmer accounts must use the mobile app."
                )

            if not db_user.is_active:
                raise UnauthorizedException("Your account has been deactivated.")

            logger.info(
                "Password login success",
                user_id=str(user_id),
                role=db_user.role.value,
            )

            from app.schemas.user import UserResponse
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=session.expires_in or 3600,
                user=UserResponse.model_validate(db_user),
            )

        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error("Password login failed", error=str(e))
            raise UnauthorizedException("Invalid email or password")

    async def get_me(self, user_id: str) -> User:
        return await self.user_repo.get_by_id(user_id)