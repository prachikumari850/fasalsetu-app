import structlog
import logging
import sys
import re
from collections.abc import Mapping
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from app.core.config import settings

REDACTED = "[REDACTED]"
_SENSITIVE_FIELD_PARTS = (
    "authorization", "apikey", "api_key", "access_token", "refresh_token",
    "id_token", "token", "password", "passwd", "secret", "service_role",
    "anon_key", "database_url", "cookie", "signed_url", "signed_token",
    "storage_url", "connection_string", "signature", "sig", "jwt",
)
_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(authorization|proxy-authorization|apikey|api_key|access_token|"
    r"refresh_token|id_token|token|password|passwd|secret|service_role|"
    r"anon_key|database_url|cookie|set-cookie|signed_url|signed_token|storage_url|"
    r"connection_string|signature|sig|jwt)"
    r"\s*([=:])\s*([^\s,;&]+)"
)
_BEARER = re.compile(r"(?i)\bBearer\s+[^\s,;]+")


def is_sensitive_field(name: object) -> bool:
    normalized = str(name).lower().replace("-", "_")
    return any(part in normalized for part in _SENSITIVE_FIELD_PARTS)


def _sanitize_url(value: str) -> str:
    """Remove URL credentials and sensitive query values without changing routing."""
    try:
        parts = urlsplit(value)
    except ValueError:
        return value
    if not parts.scheme and not parts.netloc:
        return value
    netloc = parts.hostname or ""
    if parts.port:
        netloc += f":{parts.port}"
    query = urlencode([
        (key, REDACTED if is_sensitive_field(key) else item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
    ])
    return urlunsplit((parts.scheme, netloc, parts.path, query, parts.fragment))


def sanitize_log_value(value: object) -> object:
    """Recursively redact secrets before values reach any log renderer."""
    if isinstance(value, Mapping):
        return {
            key: REDACTED if is_sensitive_field(key) else sanitize_log_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return type(value)(sanitize_log_value(item) for item in value)
    if not isinstance(value, str):
        return value
    value = _sanitize_url(value)
    value = _BEARER.sub("Bearer " + REDACTED, value)
    return _SENSITIVE_ASSIGNMENT.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{REDACTED}", value
    )


def redact_secrets(_: object, __: str, event_dict: dict) -> dict:
    return sanitize_log_value(event_dict)


class SecretRedactionFilter(logging.Filter):
    """Protect standard-library logs that do not pass through structlog."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = sanitize_log_value(record.getMessage())
        record.args = ()
        return True


def setup_logging() -> None:
    # Application debug logging remains available, but transport-level wire
    # logging is always kept at WARNING to prevent header/body disclosure.
    log_level = logging.DEBUG if not settings.is_production else logging.INFO

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            redact_secrets,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if not settings.is_production
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
        force=True,
    )
    for handler in logging.getLogger().handlers:
        handler.addFilter(SecretRedactionFilter())
    for library in (
        "httpx", "httpcore", "hpack", "h2", "supabase", "gotrue",
        "postgrest", "storage3", "realtime", "urllib3",
    ):
        logging.getLogger(library).setLevel(logging.WARNING)


logger = structlog.get_logger()
