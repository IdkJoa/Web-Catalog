import smtplib
from email.message import EmailMessage
from typing import List
from app.db.Config import settings


def send_batch_emails_smtp(subject: str, html_content: str, destination_emails: List[str]):
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)

            for email_address in destination_emails:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = smtp_user
                msg['To'] = email_address

                msg.set_content("Please enable HTML to view this email.")
                msg.add_alternative(html_content, subtype='html')

                server.send_message(msg)

    except Exception as e:
        print(f"CRITICAL: Failed to send email blast. Error: {e}")
