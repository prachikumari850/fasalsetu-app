from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from gotrue._sync.storage import SyncMemoryStorage
from app.core.config import settings
import structlog

logger = structlog.get_logger()

_auth_client: Client | None = None
_admin_client: Client | None = None


def get_supabase() -> Client:
    """
    Auth client — uses ANON KEY.
    Use for: sign_in_with_password, sign_in_with_otp, verify_otp.
    """
    global _auth_client
    if _auth_client is None:
        _auth_client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
                storage=SyncMemoryStorage(),
            ),
        )
    return _auth_client


def get_supabase_admin() -> Client:
    """
    Admin client — uses SERVICE ROLE KEY.
    Use for: storage uploads, admin operations.
    """
    global _admin_client
    if _admin_client is None:
        _admin_client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
                storage=SyncMemoryStorage(),
            ),
        )
    return _admin_client