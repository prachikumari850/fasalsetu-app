import logging

from app.core.logging import REDACTED, SecretRedactionFilter, sanitize_log_value


def test_sensitive_headers_and_nested_values_are_redacted():
    result = sanitize_log_value({
        "Authorization": "Bearer TEST_ACCESS_TOKEN",
        "headers": {"apikey": "TEST_SERVICE_ROLE_SECRET", "Cookie": "sid=test"},
        "access_token": "TEST_ACCESS_TOKEN",
        "refresh_token": "TEST_REFRESH_TOKEN",
        "password": "TEST_PASSWORD",
        "message": "upload complete",
    })
    assert result["Authorization"] == REDACTED
    assert result["headers"]["apikey"] == REDACTED
    assert result["headers"]["Cookie"] == REDACTED
    assert result["access_token"] == REDACTED
    assert result["refresh_token"] == REDACTED
    assert result["password"] == REDACTED
    assert result["message"] == "upload complete"


def test_database_and_signed_urls_do_not_expose_credentials_or_tokens():
    database_url = "postgresql+asyncpg://postgres:TEST_PASSWORD@db.example.test:5432/postgres"
    signed_url = "https://storage.example.test/object.png?token=TEST_SIGNED_TOKEN&plain=value"
    result = sanitize_log_value({
        "database_url": database_url,
        "storage_url": signed_url,
        "url": signed_url,
    })
    assert result["database_url"] == REDACTED
    assert "TEST_SIGNED_TOKEN" not in result["url"]
    assert "TEST_PASSWORD" not in str(result)
    assert "plain=value" in result["url"]
    assert result["storage_url"] == REDACTED


def test_embedded_exception_text_and_standard_logging_are_sanitized():
    raw = "Authorization: Bearer TEST_ACCESS_TOKEN password=TEST_PASSWORD"
    sanitized = sanitize_log_value(raw)
    assert "TEST_ACCESS_TOKEN" not in sanitized
    assert "TEST_PASSWORD" not in sanitized

    record = logging.LogRecord("test", logging.ERROR, __file__, 1, raw, (), None)
    assert SecretRedactionFilter().filter(record)
    assert "TEST_ACCESS_TOKEN" not in record.msg
    assert "TEST_PASSWORD" not in record.msg


def test_normal_non_sensitive_values_remain_visible():
    result = sanitize_log_value({"method": "POST", "path": "/api/v1/images/upload", "status": 201})
    assert result == {"method": "POST", "path": "/api/v1/images/upload", "status": 201}
