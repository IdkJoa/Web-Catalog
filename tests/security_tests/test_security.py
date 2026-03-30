import pytest
from datetime import timedelta
import jwt
from fastapi import HTTPException

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_email_token,
    create_password_reset_token,
    decode_token,
    get_current_active_user
)
from app.db.Config import settings


# PASSWORD ENGINE TESTS

def test_password_hashing():
    """Test that passwords hash correctly and verify properly."""
    raw_password = "SuperSecretPassword123!"
    hashed = hash_password(raw_password)

    assert raw_password != hashed
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


# TOKEN CREATION TESTS

def test_create_access_token():
    token = create_access_token(subject="user_id_123", expires_delta=timedelta(minutes=15))

    # Manually decode it to verify the insides
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user_id_123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_email_token():
    token = create_email_token(subject="user_id_456")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["type"] == "email_confirm"


def test_create_password_reset_token():
    token = create_password_reset_token(subject="user_id_789")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["type"] == "password_reset"


#  DECODE & SECURITY ENFORCEMENT TESTS

def test_decode_token_success():
    """Test that a valid token returns the correct subject."""
    token = create_access_token(subject="valid_user")
    result = decode_token(token, expected_type="access")
    assert result == "valid_user"


def test_decode_token_wrong_type_rejected():
    """Test the core security feature: blocking the wrong token type."""
    # Create an EMAIL token
    email_token = create_email_token(subject="sneaky_user")

    # Try to decode it but pretend we are asking for an ACCESS token
    result = decode_token(email_token, expected_type="access")

    # The function MUST return None because the types don't match
    assert result is None


def test_decode_tampered_token():
    """Test that the JWT library catches tampered or fake tokens."""
    # We pass total garbage text instead of a real token
    result = decode_token("this.is.not.a.real.token", expected_type="access")
    assert result is None


# DEPENDENCY TESTS (Without Database)

# To test get_current_active_user without a database, we use a fake Python object
class FakeUser:
    def __init__(self, is_active: bool, is_confirmed: bool):
        self.is_active = is_active
        self.is_confirmed = is_confirmed


def test_get_current_active_user_success():
    """Test that a fully active and confirmed user passes."""
    fake_good_user = FakeUser(is_active=True, is_confirmed=True)
    # This should return the user without raising any exceptions
    result = get_current_active_user(current_user=fake_good_user)
    assert result == fake_good_user


def test_get_current_active_user_inactive():
    """Test that inactive users are blocked."""
    fake_inactive_user = FakeUser(is_active=False, is_confirmed=True)

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=fake_inactive_user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive user"


def test_get_current_active_user_unconfirmed():
    """Test that unconfirmed emails are blocked."""
    fake_unconfirmed_user = FakeUser(is_active=True, is_confirmed=False)

    with pytest.raises(HTTPException) as exc_info:
        get_current_active_user(current_user=fake_unconfirmed_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "User email is not verified"