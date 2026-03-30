"""
SMS sending module.

Provides the SmsSender class which delivers SMS messages through an
external HTTP gateway API.  The gateway is authenticated using custom
headers (x-client-id, x-client-secret, x-scope).

A singleton instance `sms_sender` is created at module level and
imported by main.py.
"""

import httpx
import logging
import json
import uuid
from datetime import datetime
from config import get_settings

logger = logging.getLogger(__name__)


class SmsSender:
    """Async SMS sender — calls an external SMS gateway API."""
    
    def __init__(self):
        """Load SMS gateway settings from the application configuration."""
        self.settings = get_settings()
        self.api_url = self.settings.SMS_API_URL
        self.client_id = self.settings.SMS_CLIENT_ID
        self.client_secret = self.settings.SMS_CLIENT_SECRET
        self.scope = self.settings.SMS_SCOPE
        self.app_id = self.settings.SMS_APP_ID
        self.sender_name = self.settings.SMS_SENDER_NAME
        self.payload_template = self.settings.SMS_PAYLOAD_TEMPLATE
        
    async def send_sms(
        self,
        recipient: str,
        text: str,
        recipient_type: int = 0
    ) -> dict:
        """
        Send an SMS asynchronously via the external gateway API.
        
        Args:
            recipient: Phone number or ID of the recipient
            text: SMS message content
            recipient_type: 0 = phone number (default), 1 = ID (Teudat Zehut)
            
        Returns:
            Dict with keys: success (bool), message (str),
            message_id (str, on success), timestamp (str)
        """
        try:
            # ── Gateway authentication headers ─────────────────────
            headers = {
                "x-client-id": self.client_id,          # OAuth client identifier
                "x-client-secret": self.client_secret,  # OAuth client secret
                "x-scope": self.scope,                  # OAuth scope
                "Content-Type": "application/json"
            }
            
            # ── Build the JSON payload from the template ───────────
            # Escape double-quotes in dynamic values to prevent
            # broken JSON when the template is formatted.
            safe_text = text.replace('"', '\\"')
            safe_sender = self.sender_name.replace('"', '\\"')
            safe_app_id = self.app_id.replace('"', '\\"')
            safe_recipient = recipient.replace('"', '\\"')
            
            # Format the template string with sanitised values
            payload_str = self.payload_template.format(
                app_id=safe_app_id,
                sender_name=safe_sender,
                text=safe_text,
                recipient=safe_recipient,
                recipient_type=recipient_type
            )
            
            # Parse the formatted string into a Python dict
            payload = json.loads(payload_str)
            logger.info(f"Sending SMS to {recipient} via {self.api_url}")
            
            # ── Send the HTTP request to the SMS gateway ───────────
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                # Raise on 4xx/5xx responses
                response.raise_for_status()
                
                # Generate a local message ID (replace if the API returns one)
                message_id = str(uuid.uuid4())
                logger.info(f"✅ SMS sent successfully. Message ID: {message_id}")
                
                return {
                    "success": True,
                    "message": "SMS sent successfully",
                    "message_id": message_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except httpx.HTTPStatusError as error:
            logger.error(f"❌ SMS API HTTP error: {error.response.status_code} - {error.response.text}")
            return {
                "success": False,
                "message": f"SMS API error: {error.response.status_code}",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as error:
            logger.error(f"❌ Unexpected error sending SMS: {error}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(error)}",
                "timestamp": datetime.utcnow().isoformat()
            }


# Singleton instance used by all request handlers
sms_sender = SmsSender()
