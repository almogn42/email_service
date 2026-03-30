"""
Pydantic request / response models for the Email & SMS Service.

These models define the JSON schemas used for request validation and
response serialization across all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List, Dict


# ============================================================================
# Email Models
# ============================================================================

class EmailRecipient(BaseModel):
    """Single email recipient with optional display name."""
    email: EmailStr
    name: Optional[str] = None

class SendEmailRequest(BaseModel):
    """
    Request body for the /send-email and /send-email/token endpoints.
    
    You must provide EXACTLY ONE of `to` (direct email list) OR `owner` 
    (owner group name resolved from the contacts file).
    """
    to: Optional[List[EmailStr]] = Field(None, description="List of recipient email addresses")
    owner: Optional[str] = Field(None, description="Owner group name to resolve recipients from contacts file")
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body (HTML or plain text)")
    cc: Optional[List[EmailStr]] = Field(None, description="CC recipients")
    bcc: Optional[List[EmailStr]] = Field(None, description="BCC recipients")
    is_html: bool = Field(True, description="Whether body is HTML or plain text")

    @model_validator(mode="after")
    def check_exactly_one_recipient_source(self):
        has_to = bool(self.to and len(self.to) > 0)
        has_owner = bool(self.owner and len(self.owner.strip()) > 0)
        
        if has_to and has_owner:
            raise ValueError("You must provide either 'to' or 'owner', but not both.")
        if not has_to and not has_owner:
            raise ValueError("You must provide exactly one of 'to' (at least 1 email) or 'owner' (valid string).")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "to": ["recipient@example.com"],
                "subject": "Test Email",
                "body": "<h1>Hello</h1><p>This is a test email</p>",
                "cc": None,
                "bcc": None,
                "is_html": True
            }
        }

class SendEmailResponse(BaseModel):
    """Standard response returned after an email send attempt."""
    success: bool
    message: str
    message_id: Optional[str] = None
    timestamp: Optional[str] = None


class SendSmsRequest(BaseModel):
    """
    Request body for the /send-sms and /send-sms/token endpoints.
    
    You must provide EXACTLY ONE of `recipient` (direct phone/ID) OR `owner` 
    (owner group name resolved from the contacts file).

    recipient_type controls how the gateway interprets the recipient value:
      0 = phone number (default)
      1 = ID number (Teudat Zehut)
    """
    recipient: Optional[str] = Field(None, description="Phone number or ID of the recipient")
    owner: Optional[str] = Field(None, description="Owner group name to resolve recipients from contacts file")
    text: str = Field(..., min_length=1, description="SMS message content")
    recipient_type: int = Field(0, description="0 for standard, 1 for ID Teudat Zehut")

    @model_validator(mode="after")
    def check_exactly_one_recipient_source(self):
        has_recipient = bool(self.recipient and len(self.recipient.strip()) > 0)
        has_owner = bool(self.owner and len(self.owner.strip()) > 0)
        
        if has_recipient and has_owner:
            raise ValueError("You must provide either 'recipient' or 'owner', but not both.")
        if not has_recipient and not has_owner:
            raise ValueError("You must provide exactly one of 'recipient' (valid string) or 'owner' (valid string).")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "0501234567",
                "text": "Hello this is a test SMS",
                "recipient_type": 0
            }
        }

class SendSmsResponse(BaseModel):
    """Standard response returned after an SMS send attempt."""
    success: bool
    message: str
    message_id: Optional[str] = None       # UUID generated on success
    timestamp: Optional[str] = None        # ISO-8601 UTC timestamp


# ============================================================================
# Contacts Upload
# ============================================================================

class UploadContactsRequest(BaseModel):
    """
    Request body for the /upload-contacts endpoint.
    
    Expects a dict with an 'Owners' key mapping group names to contacts.
    """
    Owners: Dict[str, Dict[str, Dict[str, str]]] = Field(
        ..., description="Owner groups with contact details (email, phone_number)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "Owners": {
                    "it_team": {
                        "almog": {
                            "email": "almog@example.com",
                            "phone_number": "0501234567"
                        }
                    }
                }
            }
        }


# ============================================================================
# Service Status
# ============================================================================

class ServiceStatus(BaseModel):
    """Response model for the /status health check endpoint."""
    status: str      # e.g. "operational"
    service: str     # Service display name from settings
    version: str     # Semantic version string
