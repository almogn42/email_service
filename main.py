"""
Main application entry point for the Email & SMS Service API.

Defines all FastAPI routes, middleware, and exception handlers.
Run directly with: python main.py
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from typing import Optional
from datetime import datetime

from config import get_settings
from models import SendEmailRequest, SendEmailResponse, SendSmsRequest, SendSmsResponse, ServiceStatus
from email_sender import email_sender
from sms_sender import sms_sender
from auth import verify_basic_auth, verify_oauth_token

# ── Logging configuration ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── FastAPI application instance ──────────────────────────────────
app = FastAPI(
    title="Email & SMS Service API",
    description="Service to send emails and SMS via web requests with Basic Auth and OAuth support",
    version="1.0.0"
)

# ── CORS Middleware ────────────────────────────────────────────────
# Cross-Origin Resource Sharing controls which websites/domains can
# call this API from a browser.
#
# CURRENT SETTING: allow_origins=["*"] permits ANY website to call
# this API. This is fine during development but is a security risk
# in production — a malicious website could make requests on behalf
# of authenticated users.
#
# HOW TO RESTRICT (production):
#   Replace ["*"] with a list of allowed origin URLs, for example:
#
#   allow_origins=[
#       "https://your-frontend.example.com",
#       "https://admin-panel.example.com",
#   ]
#
#   - Each origin must include the scheme (https://) and domain.
#   - Do NOT include a trailing slash.
#   - Subdomains are separate origins (app.example.com ≠ example.com).
#   - You can also load these from an env variable:
#       allow_origins=settings.ALLOWED_ORIGINS  (add ALLOWED_ORIGINS to config.py)
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # ← Replace with explicit origins in production
    allow_credentials=True,
    allow_methods=["*"],            # Or restrict to ["GET", "POST"] if needed
    allow_headers=["*"],            # Or restrict to ["Authorization", "Content-Type"]
)

# Cached settings instance (shared across all handlers)
settings = get_settings()

# ============================================================================
# Health Check & Status Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint — no authentication required."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/status", response_model=ServiceStatus, tags=["Health"])
async def get_status(username: str = Depends(verify_basic_auth)):
    """Get service status — requires Basic Auth."""
    return ServiceStatus(
        status="operational",
        service=settings.SERVICE_NAME,
        version="1.0.0"
    )

# ============================================================================
# Email Endpoints
# ============================================================================

@app.post("/send-email", response_model=SendEmailResponse, tags=["Email"])
async def send_email(
    request: SendEmailRequest,
    username: str = Depends(verify_basic_auth)
):
    """
    Send an email using Basic Authentication.
    
    Requires HTTP Basic Authentication with username and password.
    
    **Authentication:** Use Basic Auth (username:password in Authorization header)
    
    Example with curl:
    ```
    curl -X POST http://localhost:8000/send-email \\
      -H "Content-Type: application/json" \\
      -u "admin:changeme" \\
      -d '{
        "to": ["recipient@example.com"],
        "subject": "Test Email",
        "body": "<h1>Hello</h1>",
        "is_html": true
      }'
    ```
    """
    logger.info(f"Email send request from user: {username}")
    logger.info(f"Recipients: {request.to}")
    
    result = await email_sender.send_email(
        to_addresses=request.to,
        subject=request.subject,
        body=request.body,
        cc_addresses=request.cc,
        bcc_addresses=request.bcc,
        is_html=request.is_html
    )
    
    if not result["success"]:
        logger.error(f"Failed to send email: {result['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    logger.info(f"Email sent successfully. Message ID: {result.get('message_id')}")
    
    return SendEmailResponse(
        success=result["success"],
        message=result["message"],
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp")
    )

@app.post("/send-email/token", response_model=SendEmailResponse, tags=["Email"])
async def send_email_with_token(
    request: SendEmailRequest,
    token: str = Depends(verify_oauth_token)
):
    """
    Send an email using Bearer Token (OAuth/API Key) Authentication.
    
    Requires an Authorization header with Bearer token.
    
    **Authentication:** Use Bearer Token in Authorization header
    
    Example with curl:
    ```
    curl -X POST http://localhost:8000/send-email/token \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer your-api-token-here" \\
      -d '{
        "to": ["recipient@example.com"],
        "subject": "Test Email",
        "body": "<h1>Hello</h1>",
        "is_html": true
      }'
    ```
    """
    logger.info(f"Email send request with token: {token[:10]}...")
    logger.info(f"Recipients: {request.to}")
    
    result = await email_sender.send_email(
        to_addresses=request.to,
        subject=request.subject,
        body=request.body,
        cc_addresses=request.cc,
        bcc_addresses=request.bcc,
        is_html=request.is_html
    )
    
    if not result["success"]:
        logger.error(f"Failed to send email: {result['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    logger.info(f"Email sent successfully. Message ID: {result.get('message_id')}")
    
    return SendEmailResponse(
        success=result["success"],
        message=result["message"],
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp")
    )


# ============================================================================
# SMS Endpoints
# ============================================================================

@app.post("/send-sms", response_model=SendSmsResponse, tags=["SMS"])
async def send_sms(
    request: SendSmsRequest,
    username: str = Depends(verify_basic_auth)
):
    """
    Send an SMS using Basic Authentication.
    
    Example with curl:
    ```
    curl -X POST http://localhost:8000/send-sms \\
      -H "Content-Type: application/json" \\
      -u "admin:changeme" \\
      -d '{
        "recipient": "0501234567",
        "text": "Hello from the API",
        "recipient_type": 0
      }'
    ```
    """
    logger.info(f"SMS send request from user: {username}")
    logger.info(f"Recipient: {request.recipient}")
    
    result = await sms_sender.send_sms(
        recipient=request.recipient,
        text=request.text,
        recipient_type=request.recipient_type
    )
    
    if not result["success"]:
        logger.error(f"Failed to send SMS: {result['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    logger.info(f"SMS sent successfully. Message ID: {result.get('message_id')}")
    
    return SendSmsResponse(
        success=result["success"],
        message=result["message"],
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp")
    )

@app.post("/send-sms/token", response_model=SendSmsResponse, tags=["SMS"])
async def send_sms_with_token(
    request: SendSmsRequest,
    token: str = Depends(verify_oauth_token)
):
    """
    Send an SMS using Bearer Token (OAuth/API Key) Authentication.
    
    Example with curl:
    ```
    curl -X POST http://localhost:8000/send-sms/token \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer your-api-token-here" \\
      -d '{
        "recipient": "0501234567",
        "text": "Hello from the API",
        "recipient_type": 0
      }'
    ```
    """
    logger.info(f"SMS send request with token: {token[:10]}...")
    logger.info(f"Recipient: {request.recipient}")
    
    result = await sms_sender.send_sms(
        recipient=request.recipient,
        text=request.text,
        recipient_type=request.recipient_type
    )
    
    if not result["success"]:
        logger.error(f"Failed to send SMS: {result['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    logger.info(f"SMS sent successfully. Message ID: {result.get('message_id')}")
    
    return SendSmsResponse(
        success=result["success"],
        message=result["message"],
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp")
    )

# ============================================================================
# Admin Endpoints
# ============================================================================

@app.get("/tokens", tags=["Admin"])
async def get_tokens(username: str = Depends(verify_basic_auth)):
    """
    Retrieve all configured API (Bearer) tokens in clear text.
    
    **Restricted to the "admin" user only.**  
    Intended for admin/debugging purposes — do not expose in production
    without additional safeguards.
    
    **Authentication:** Basic Auth (admin user only)
    
    Example with curl:
    ```
    curl -u admin:changeme http://localhost:8000/tokens
    ```
    """
    # Only the "admin" user is allowed to view tokens
    if username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the admin user can access this endpoint"
        )

    return {
        "tokens": settings.API_TOKENS,
        "count": len(settings.API_TOKENS),
        "authenticated_user": username,
    }

# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler — adds timestamp to error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler — logs the full traceback."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        },
    )

# ============================================================================
# Root Endpoint
