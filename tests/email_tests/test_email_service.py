import pytest
from unittest.mock import patch, AsyncMock

from app.services.email_service import EmailService

# TEST: VERIFICATION EMAIL
# We patch the exact method that reaches out to the internet.
# Using new_callable=AsyncMock is required because send_message is an 'async def' function!
@pytest.mark.asyncio
@patch("app.services.email_service.FastMail.send_message", new_callable=AsyncMock)
async def test_send_verification_email(mock_send_message):
    """Test that the verification email formats the message and token correctly."""

    # 1. Initialize the service
    email_service = EmailService()
    test_email = "new_admin@example.com"
    test_token = "secure_verification_token_123"

    await email_service.send_verification_email(email_to=test_email, token=test_token)

    # 3. Verify the mock was triggered exactly once so we know an email "sent"
    mock_send_message.assert_called_once()

    # 4. Extract the MessageSchema that was handed to the mock
    # call_args[0][0] captures the very first argument passed into send_message
    sent_message = mock_send_message.call_args[0][0]

    # 5. Verify the contents of the email
    assert sent_message.subject == "Verify your Admin Account for Web'Catalog"
    assert sent_message.recipients[0].email == test_email

    # Verify the token actually made it into the HTML body!
    assert test_token in sent_message.body


# PASSWORD RESET EMAIL
@pytest.mark.asyncio
@patch("app.services.email_service.FastMail.send_message", new_callable=AsyncMock)
async def test_send_reset_email(mock_send_message):
    """Test that the password reset email formats the message and token correctly."""

    email_service = EmailService()
    test_email = "forgetful_admin@example.com"
    test_token = "secure_reset_token_456"

    await email_service.send_reset_email(email_to=test_email, token=test_token)

    mock_send_message.assert_called_once()

    sent_message = mock_send_message.call_args[0][0]

    assert sent_message.subject == "Reset your CMS Password"
    assert sent_message.recipients[0].email == test_email

    # Verify the token is embedded in the HTML link
    assert test_token in sent_message.body