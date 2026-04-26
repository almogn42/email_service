"""
Configuration module for the Email & SMS Service.

Loads settings from environment variables and .env file using Pydantic.
Handles automatic password hashing for basic auth users on startup.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
import json
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.
    All fields can be overridden via environment variables or .env entries.
    """

    # ── SMTP (Email) Settings ──────────────────────────────────────
    SMTP_SERVER: str = "smtp.gmail.com"         # SMTP server hostname
    SMTP_PORT: int = 587                        # 587 = STARTTLS, 465 = implicit SSL, 25 = plain text
    SMTP_TLS_MODE: str = "auto"                 # "starttls", "implicit", "none", or "auto"
    SMTP_USERNAME: str = ""                     # Login username for the SMTP server
    SMTP_PASSWORD: str = ""                     # Login password (use app-password for Gmail)
    SMTP_FROM_EMAIL: str = ""                   # "From" address shown to recipients
    
    # ── Custom SSL CA / Verification Settings ──
    SMTP_SSL_VERIFY: bool = True                # Set to False to disable SSL certificate verification
    SMTP_CA_CERT_PATH: str = ""                 # Path to a custom CA certificate file (e.g. /path/to/org_ca.pem)

    # ── General Service Settings ───────────────────────────────────
    SERVICE_NAME: str = "Email Service"         # Display name used in /status and root
    DEBUG: bool = False                         # Enable debug logging when True
    
    # ── SMS Gateway Settings ───────────────────────────────────────
    SMS_API_URL: str = "http://localhost:8080/sms-api"  # External SMS API endpoint
    SMS_CLIENT_ID: str = ""                     # OAuth client ID for the SMS gateway
    SMS_CLIENT_SECRET: str = ""                 # OAuth client secret for the SMS gateway
    SMS_SCOPE: str = ""                         # OAuth scope for the SMS gateway
    SMS_APP_ID: str = ""                        # Application ID sent in SMS payload
    SMS_SENDER_NAME: str = ""                   # Sender name shown to SMS recipients

    # Template for the SMS JSON payload.
    # Placeholders: {app_id}, {sender_name}, {text}, {recipient}, {recipient_type}
    SMS_PAYLOAD_TEMPLATE: str = '{{"applicationId": "{app_id}", "smsSenderName": "{sender_name}", "smsMessageText": "{text}", "recipient": "{recipient}", "recipientType": {recipient_type}}}'
    
    # ── SMS SSL / Verification Settings ────────────────────────────
    SMS_SSL_VERIFY: bool = True                 # Set to False to disable SSL certificate verification for SMS API
    SMS_CA_CERT_PATH: str = ""                  # Path to a custom CA certificate file for SMS API

    # ── Basic Auth Users ───────────────────────────────────────────
    # Dictionary mapping username → password (plain-text or hashed).
    # Plain-text passwords are automatically hashed on first startup.
    BASIC_AUTH_USERS: dict = {
        "admin": "changeme",  # Change these credentials!
    }
    
    @field_validator('BASIC_AUTH_USERS')
    @classmethod
    def hash_passwords(cls, users_dict: dict) -> dict:
        """
        Hash any plain-text passwords and persist hashed values back to .env.

        Called once during Settings initialization. Passwords that are already
        hashed (start with '$pbkdf2') are left untouched.
        """
        # Import here to avoid circular import (auth.py imports config.py)
        from auth import get_password_hash

        hashed_users = {}
        has_plain_text_passwords = False

        for username, password in users_dict.items():
            is_already_hashed = password.startswith('$pbkdf2')
            if is_already_hashed:
                hashed_users[username] = password
            else:
                hashed_users[username] = get_password_hash(password)
                has_plain_text_passwords = True

        # Persist hashed passwords back to .env so they aren't re-hashed next time
        if has_plain_text_passwords:
            env_file_path = ".env"
            if os.path.exists(env_file_path):
                try:
                    with open(env_file_path, "r", encoding="utf-8") as env_file:
                        env_lines = env_file.readlines()

                    with open(env_file_path, "w", encoding="utf-8") as env_file:
                        for line in env_lines:
                            if line.strip().startswith("BASIC_AUTH_USERS="):
                                # Replace the line with the hashed version
                                hashed_json = json.dumps(hashed_users)
                                env_file.write(f"BASIC_AUTH_USERS={hashed_json}\n")
                            else:
                                env_file.write(line)
                except Exception as error:
                    print(f"Warning: Could not update .env with hashed passwords: {error}")

        return hashed_users
    
    # ── API / Bearer Tokens ────────────────────────────────────────
    # List of valid tokens accepted by the Bearer auth endpoints.
    API_TOKENS: list = ["your-api-token-here"]
    
    class Config:
        env_file = ".env"           # Path to the .env file
        case_sensitive = True       # Environment variable names are case-sensitive

@lru_cache()
def get_settings():
    """Return a cached Settings instance.
    
    Thanks to @lru_cache, Settings() is created only ONCE per process.
    This means hash_passwords runs once on first call, and all subsequent
    calls reuse the same instance with already-hashed passwords in memory.
    """
    return Settings()
