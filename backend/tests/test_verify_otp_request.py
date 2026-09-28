import pytest
from pydantic import ValidationError

from app.schemas.user import VerifyOtpRequest


def make_request(otp: str) -> VerifyOtpRequest:
    return VerifyOtpRequest(email="farmer@example.com", otp=otp)


@pytest.mark.parametrize("otp", ["123456", "012345"])
def test_verify_otp_request_accepts_six_ascii_digits(otp: str) -> None:
    assert make_request(otp).otp == otp


@pytest.mark.parametrize(
    "otp",
    ["12345", "1234567", "12345678", "१२३४५६", "abcdef", "123a56"],
)
def test_verify_otp_request_rejects_non_six_ascii_digit_values(otp: str) -> None:
    with pytest.raises(ValidationError, match="OTP must be exactly 6 digits"):
        make_request(otp)


def test_verify_otp_request_trims_before_validating() -> None:
    assert make_request("  012345\t").otp == "012345"
