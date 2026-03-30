import smtplib
import logging
from email.message import EmailMessage
from typing import List
from app.db.Config import settings

logger = logging.getLogger(__name__)

def send_batch_emails_smtp(subject: str, html_content: str, destination_emails: List[str]):
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    logger.info(f"Starting batch email send to {len(destination_emails)} subscribers")
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)

            for email_address in destination_emails:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = smtp_user
                    msg['To'] = email_address

                    msg.set_content("Please enable HTML to view this email.")
                    msg.add_alternative(html_content, subtype='html')

                    server.send_message(msg)
                    logger.debug(f"Email sent successfully to {email_address}")
                except Exception as sub_e:
                    logger.error(f"Failed to send email to {email_address}: {sub_e}")

        logger.info("Finished batch email send")

    except Exception as e:
        logger.error(f"CRITICAL: Failed to connect to SMTP or login. Error: {e}")
        raise
