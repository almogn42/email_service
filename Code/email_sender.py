"""
SMTP email sending module.

Provides the SMTPEmailSender class which handles asynchronous email
delivery through any standard SMTP server.  Supports both STARTTLS
(port 587) and implicit SSL (port 465).

A singleton instance `email_sender` is created at module level and
imported by main.py.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import get_settings
from typing import List, Optional
from datetime import datetime
import uuid
import ssl

logger = logging.getLogger(__name__)


class SMTPEmailSender:
    """Async SMTP email sender — one instance shared across all requests."""
    
    def __init__(self):
        """Load SMTP connection details from the application settings."""
        self.settings = get_settings()
        self.smtp_server = self.settings.SMTP_SERVER
        self.smtp_port = self.settings.SMTP_PORT
        self.smtp_username = self.settings.SMTP_USERNAME
        self.smtp_password = self.settings.SMTP_PASSWORD
        self.from_email = self.settings.SMTP_FROM_EMAIL
        self.smtp_tls_mode = self.settings.SMTP_TLS_MODE.lower()
    
    async def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
        is_html: bool = True
    ) -> dict:
        """
        Send an email asynchronously via SMTP.
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject line
            body: Email body content (HTML or plain text)
            cc_addresses: Optional list of CC recipients
            bcc_addresses: Optional list of BCC recipients
            is_html: True → HTML email, False → plain text
        
        Returns:
            Dict with keys: success (bool), message (str),
            message_id (str, on success), timestamp (str)
        """
        try:
            # ── Build the MIME message ─────────────────────────────
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = ", ".join(to_addresses)
            
            if cc_addresses:
                message["Cc"] = ", ".join(cc_addresses)
            
            # Attach body as HTML or plain text
            mime_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, mime_type, "utf-8"))
            
            # ── Collect all recipients (To + CC + BCC) ─────────────
            all_recipients = to_addresses.copy()
            if cc_addresses:
                all_recipients.extend(cc_addresses)
            if bcc_addresses:
                all_recipients.extend(bcc_addresses)
            
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}")
            
            # ── Determine TLS mode ─────────────────────────────────
            tls_mode = self.smtp_tls_mode
            if tls_mode == "auto":
                if self.smtp_port == 587:
                    tls_mode = "starttls"
                elif self.smtp_port == 465:
                    tls_mode = "implicit"
                elif self.smtp_port == 25:
                    tls_mode = "none"
                else:
                    raise ValueError(f"Cannot auto-determine TLS over port {self.smtp_port}. Please set SMTP_TLS_MODE explicitly.")

            # ── Create SSL context for encrypted connection ────────
            ssl_context = ssl.create_default_context()

            # 1. Disable Verification (Ignore cert errors)
            if not self.settings.SMTP_SSL_VERIFY:
                logger.warning("SMTP SSL verification is DISABLED (SMTP_SSL_VERIFY=False)")
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
            # 2. Use Custom CA File (Verify against organization CA)
            elif self.settings.SMTP_CA_CERT_PATH:
                logger.info(f"Loading custom CA cert from {self.settings.SMTP_CA_CERT_PATH}")
                ssl_context.load_verify_locations(cafile=self.settings.SMTP_CA_CERT_PATH)


            # ── Mode: STARTTLS (upgrade plain → encrypted) ─────────
            if tls_mode == "starttls":
                logger.info(f"Using STARTTLS on port {self.smtp_port}")
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    timeout=10,
                    start_tls=True,
                    tls_context=ssl_context,
                    validate_certs=self.settings.SMTP_SSL_VERIFY
                ) as smtp:
                    if self.smtp_username:
                        logger.info(f"Logging in as {self.smtp_username}")
                        await smtp.login(self.smtp_username, self.smtp_password)
                    logger.info(f"Sending email to {len(all_recipients)} recipients")
                    await smtp.sendmail(self.from_email, all_recipients, message.as_string())
            
            # ── Mode: Implicit SSL (encrypted from the start) ──────
            elif tls_mode == "implicit":
                logger.info(f"Using implicit SSL on port {self.smtp_port}")
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    timeout=10,
                    use_tls=True,
                    tls_context=ssl_context,
                    validate_certs=self.settings.SMTP_SSL_VERIFY
                ) as smtp:
                    if self.smtp_username:
                        logger.info(f"Logging in as {self.smtp_username}")
                        await smtp.login(self.smtp_username, self.smtp_password)
                    logger.info(f"Sending email to {len(all_recipients)} recipients")
                    await smtp.sendmail(self.from_email, all_recipients, message.as_string())
            
            # ── Mode: None (plain text, no encryption) ─────────────
            elif tls_mode == "none":
                logger.info(f"Using NO TLS (plain text) on port {self.smtp_port}")
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    timeout=10
                ) as smtp:
                    if self.smtp_username:
                        logger.warning(f"Logging in over plain text (INSECURE) as {self.smtp_username}")
                        await smtp.login(self.smtp_username, self.smtp_password)
                    logger.info(f"Sending email to {len(all_recipients)} recipients")
                    await smtp.sendmail(self.from_email, all_recipients, message.as_string())

            else:
                raise ValueError(f"Unsupported SMTP_TLS_MODE: {tls_mode}")
            
            # Generate a local message ID (SMTP server may assign its own)
            message_id = str(uuid.uuid4())
            logger.info(f"✅ Email sent successfully. Message ID: {message_id}")
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "message_id": message_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except aiosmtplib.SMTPAuthenticationError as error:
            logger.error(f"❌ SMTP Authentication failed: {error}")
            return {
                "success": False,
                "message": "SMTP authentication failed. Check credentials or use Gmail App Password.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except aiosmtplib.SMTPException as error:
            logger.error(f"❌ SMTP error: {error}")
            return {
                "success": False,
                "message": f"SMTP error: {str(error)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as error:
            logger.error(f"❌ Unexpected error sending email: {error}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(error)}",
                "timestamp": datetime.utcnow().isoformat()
            }


# Singleton instance used by all request handlers
email_sender = SMTPEmailSender()
