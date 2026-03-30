import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

# Adjust these imports to match your actual file paths
from app.models.models import AdminUser
from app.schemas.schemas import AdminUserCreate
from app.services.auth.register_user import admin


# TEST: CREATE USER

# We use @patch to intercept the security.hash_password function
# so we don't waste CPU cycles calculating real hashes during testing.
@patch("app.core.security.hash_password")
def test_create_admin_user(mock_hash_password):
    """Test that creating a user hashes the password and sets default flags."""

    # Set up our mock database session and mock hasher
    mock_db = MagicMock(spec=Session)
    mock_hash_password.return_value = "fake_hashed_password_123@H"

    # Create the incoming Pydantic schema
    user_in = AdminUserCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="MySecretPassword!1@"
    )

    created_user = admin.create(db=mock_db, obj_in=user_in)

    assert created_user.email == "john@example.com"
    assert created_user.password == "fake_hashed_password_123@H"
    assert created_user.is_active is True
    assert created_user.is_confirmed is False

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


# TEST: GET BY EMAIL
def test_get_user_by_email_found():
    """Test retrieving a user by email when they exist."""
    mock_db = MagicMock(spec=Session)

    # Create the fake database row we want to "find"
    fake_user = AdminUser(email="admin@example.com", first_name="Admin")

    # Tell the mock DB to return our fake user when scalar_one_or_none() is called
    mock_db.execute.return_value.scalar_one_or_none.return_value = fake_user

    # Execute the service
    result = admin.get_by_email(db=mock_db, email="admin@example.com")

    assert result is not None
    assert result.email == "admin@example.com"


def test_get_user_by_email_not_found():
    """Test retrieving a user when the email does not exist in the database."""
    mock_db = MagicMock(spec=Session)

    # Tell the mock DB to return None (simulating an empty query)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    result = admin.get_by_email(db=mock_db, email="ghost@example.com")

    assert result is None


# 3. TEST: CONFIRM USER
def test_confirm_user():
    """Test that the confirm method flips the boolean flag and saves to the DB."""
    mock_db = MagicMock(spec=Session)

    # Set up an unconfirmed user
    unconfirmed_user = AdminUser(email="test@example.com", is_confirmed=False)

    # Execute the service
    confirmed_user = admin.confirm_user(db=mock_db, db_obj=unconfirmed_user)

    # Verify the logic
    assert confirmed_user.is_confirmed is True

    # Verify the database saved the change
    mock_db.add.assert_called_once_with(unconfirmed_user)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(unconfirmed_user)