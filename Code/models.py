"""
Pydantic request / response models for the Email & SMS Service.

These models define the JSON schemas used for request validation and
response serialization across all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


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
    
    At least one recipient in `to` is required. The body can be HTML
    (default) or plain text depending on the `is_html` flag.
    """
    to: List[EmailStr] = Field(..., min_length=1, description="List of recipient email addresses")
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body (HTML or plain text)")
    cc: Optional[List[EmailStr]] = Field(None, description="CC recipients")
    bcc: Optional[List[EmailStr]] = Field(None, description="BCC recipients")
    is_html: bool = Field(True, description="Whether body is HTML or plain text")
    
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

class ServiceStatus(BaseModel):
    """Service status response."""
    status: str
    service: str
    version: str

class SendSmsRequest(BaseModel):
    """
    Request body for the /send-sms and /send-sms/token endpoints.
    
    recipient_type controls how the gateway interprets the recipient value:
      0 = phone number (default)
      1 = ID number (Teudat Zehut)
    """
    recipient: str = Field(..., min_length=1, description="Phone number or ID of the recipient")
    text: str = Field(..., min_length=1, description="SMS message content")
    recipient_type: int = Field(0, description="0 for standard, 1 for ID Teudat Zehut")
    
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
# Service Status
# ============================================================================

class ServiceStatus(BaseModel):
    """Response model for the /status health check endpoint."""
    status: str      # e.g. "operational"
    service: str     # Service display name from settings
    version: str     # Semantic version string
