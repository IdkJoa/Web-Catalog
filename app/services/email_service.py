from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.db.Config import settings

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.EMAILS_FROM,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.mailer = FastMail(self.conf)

    async def send_verification_email(self, email_to: EmailStr, token: str):
        frontend = settings.FRONTEND_URL or "http://localhost:8000"
        verification_link = f"{frontend}/auth/verify-email/{token}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <h2>Welcome to your Web Catalog</h2>
            <p>You recently registered for an admin account. Please click the button below to verify your email address.</p>
            <a href="{verification_link}" style="display: inline-block; padding: 10px 20px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px;">
                Verify Email
            </a>
        </div>
        """

        message = MessageSchema(
            subject="Verify your Admin Account for Web'Catalog",
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html
        )

        await self.mailer.send_message(message)

    async def send_reset_email(self, email_to: str, token: str):
        frontend = settings.FRONTEND_URL or "http://localhost:3000"
        reset_link = f"{frontend}/reset-password?token={token}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <h2>Password Reset Request</h2>
            <p>Click the link below to securely reset your password. This link expires in 15 minutes.</p>
            <a href="{reset_link}" style="padding: 10px 20px; background-color: #dc3545; color: white; text-decoration: none;">
                Reset Password
            </a>
            <p>If you didn't request this, you can safely ignore this email.</p>
        </div>
        """

        message = MessageSchema(
            subject="Reset your CMS Password",
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html
        )
        await self.mailer.send_message(message)