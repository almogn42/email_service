# 📧 Email & SMS Service — Complete Project Overview

## Project Summary

A production-ready **FastAPI-based microservice** that:
- ✅ Listens for HTTP web requests
- ✅ Supports **Basic Authentication** (username/password)
- ✅ Supports **OAuth/Bearer Token Authentication** (API keys)
- ✅ Creates and sends SMTP emails based on requests
- ✅ Sends SMS messages via an external HTTP gateway
- ✅ Admin endpoint to view API tokens (admin-only)
- ✅ Handles async concurrent operations efficiently
- ✅ Auto-generates API documentation (Swagger UI)
- ✅ Auto-hashes passwords on first startup

---

## 📁 Project Files

### Core Application Files

#### `main.py` (Main Application)
The FastAPI application entry point containing:
- API route handlers for email, SMS, admin, and health endpoints
- Request/response handling
- Exception handlers
- CORS middleware configuration
- Comprehensive docstrings with curl examples

**Key Endpoints:**
- `GET /health` — Health check (no auth)
- `GET /` — Root with service info (no auth)
- `GET /status` — Service status (requires Basic Auth)
- `POST /send-email` — Send email (requires Basic Auth)
- `POST /send-email/token` — Send email (requires Bearer Token)
- `POST /send-sms` — Send SMS (requires Basic Auth)
- `POST /send-sms/token` — Send SMS (requires Bearer Token)
- `GET /tokens` — View API tokens (admin-only, Basic Auth)
- `GET /docs` — Swagger UI (auto-generated)
- `GET /redoc` — ReDoc documentation (auto-generated)

#### `config.py` (Configuration)
Centralized configuration management with:
- SMTP settings (server, port, credentials)
- SMS gateway settings (API URL, client ID/secret, scope, app ID, sender name)
- SMS payload template (configurable JSON structure)
- Basic auth users dictionary (auto-hashed on startup)
- API tokens list
- Service metadata
- Support for `.env` file and environment variables

#### `auth.py` (Authentication)
Authentication logic with three dependency functions:
- `verify_basic_auth()` — Validates HTTP Basic Auth credentials against hashed passwords
- `verify_oauth_token()` — Validates Bearer token against allowed token list
- `verify_auth()` — Combined auth (accepts either method)
- Password hashing utilities using PBKDF2-SHA256

#### `models.py` (Data Validation)
Pydantic models for type safety:
- `SendEmailRequest` — Validates incoming email requests
- `SendEmailResponse` — Standardizes email responses
- `SendSmsRequest` — Validates incoming SMS requests
- `SendSmsResponse` — Standardizes SMS responses
- `ServiceStatus` — Service status response
- `EmailRecipient` — Email recipient model

#### `email_sender.py` (SMTP Handler)
Async SMTP email sending:
- `SMTPEmailSender` class with async email sending
- Support for STARTTLS (port 587) and implicit SSL (port 465)
- CC and BCC recipients
- HTML and plain text email support
- Comprehensive error handling

#### `sms_sender.py` (SMS Gateway Handler)
Async SMS sending via external API:
- `SmsSender` class with async HTTP-based SMS sending
- Configurable JSON payload template
- Gateway authentication via custom headers (x-client-id, x-client-secret, x-scope)
- Support for phone number and ID (Teudat Zehut) recipients

---

### Configuration Files

#### `.env.example`
Template for environment configuration including SMTP and SMS settings.

#### `requirements.txt`
Python dependencies:
- FastAPI: Web framework
- uvicorn: ASGI server
- aiosmtplib: Async SMTP client
- httpx: Async HTTP client (SMS gateway)
- pydantic / pydantic-settings: Data validation & config
- python-jose: JWT/OAuth support
- passlib: Password hashing (PBKDF2)
- pytest / pytest-asyncio: Testing

---

### Deployment Files

#### `Dockerfile`
- Python 3.11 slim base image
- Dependency installation
- Health check configuration
- Port 8000 exposed

#### `docker-compose.yml`
- Service definition with email + SMS environment variables
- Port mapping (8000:8000)
- Volume mounts for logs
- Restart policy and health check

---

## 📊 API Endpoints Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/health` | None | Health check |
| GET | `/` | None | Service info |
| GET | `/status` | Basic | Get service status |
| POST | `/send-email` | Basic | Send email (Basic Auth) |
| POST | `/send-email/token` | Bearer | Send email (Token Auth) |
| POST | `/send-sms` | Basic | Send SMS (Basic Auth) |
| POST | `/send-sms/token` | Bearer | Send SMS (Token Auth) |
| GET | `/tokens` | Basic (admin) | View API tokens |
| GET | `/docs` | None | Swagger UI |
| GET | `/redoc` | None | ReDoc documentation |

---

## 📋 Request/Response Examples

### Send Email Request
```json
{
  "to": ["recipient@example.com"],
  "subject": "Important Message",
  "body": "<h1>Hello</h1><p>This is important</p>",
  "cc": ["manager@example.com"],
  "bcc": ["archive@example.com"],
  "is_html": true
}
```

### Send SMS Request
```json
{
  "recipient": "0501234567",
  "text": "Hello from the API",
  "recipient_type": 0
}
```

### Success Response (Email or SMS)
```json
{
  "success": true,
  "message": "Email sent successfully",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-25T10:30:45.123456"
}
```

### Tokens Response
```json
{
  "tokens": ["my-secure-token-123", "another-secure-token"],
  "count": 2,
  "authenticated_user": "admin"
}
```

### Error Response
```json
{
  "detail": "Invalid credentials",
  "status_code": 401,
  "timestamp": "2026-03-25T10:30:45.123456"
}
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
Copy `.env.example` to `.env` and configure SMTP + SMS settings.

### 3. Run Service
```bash
python main.py
```

### 4. Test API
Visit: http://localhost:8000/docs (Swagger UI)

---

## 🐳 Docker Deployment

```bash
docker build -t email-sms-service .
docker run -p 8000:8000 --env-file .env email-sms-service
# or
docker-compose up
```

---

## 🔒 Security Checklist

- [ ] Change default credentials in `.env`
- [ ] Use strong API tokens (32+ characters)
- [ ] Enable HTTPS in production (reverse proxy)
- [ ] Restrict CORS origins
- [ ] Implement rate limiting
- [ ] Rotate API tokens regularly
- [ ] Monitor `/tokens` endpoint usage

---

## Version History

**v1.1.0** — SMS & Admin Update
- Added SMS sending via external gateway API
- Added `GET /tokens` admin endpoint
- Auto-hashing of Basic Auth passwords on startup
- Improved code comments and readability

**v1.0.0** — Initial Release
- FastAPI-based email service
- Basic Auth & Bearer Token support
- SMTP email sending
- Auto-generated API documentation
- Docker support

---

## License

MIT License — Free to use in your projects
