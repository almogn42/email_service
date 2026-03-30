# Email & SMS Service API

A FastAPI-based microservice for sending **emails** and **SMS messages** via web requests with support for **Basic Authentication** and **Bearer Token (OAuth) Authentication**.

## Features

✅ **Dual Authentication Methods**
- HTTP Basic Authentication (username/password)
- Bearer Token Authentication (API key)

✅ **SMTP Email Sending**
- Support for HTML and plain text emails
- CC and BCC recipients
- Async SMTP for high performance

✅ **SMS Sending**
- External SMS gateway integration via HTTP
- Configurable payload template
- Support for phone-number and ID-based recipients

✅ **Admin Endpoint**
- `GET /tokens` — view all API tokens (admin-only, Basic Auth)

✅ **Auto-Generated API Documentation**
- Swagger UI at `/docs`
- ReDoc at `/redoc`

✅ **Production Ready**
- Comprehensive error handling
- Structured logging
- CORS support
- Input validation with Pydantic
- Password hashing (PBKDF2-SHA256)

---

## Installation

### 1. Clone or navigate to project directory
```bash
cd email_service
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
# Copy example config
cp .env.example .env

# Edit .env with your SMTP and SMS settings
# For Gmail:
# 1. Enable 2-factor authentication
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Use the 16-character password in SMTP_PASSWORD
```

---

## Running the Service

### Start the server
```bash
python main.py
```

Server will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### 1. Health Check (No Auth Required)
```bash
curl http://localhost:8000/health
```

### 2. Send Email with Basic Auth

**Endpoint:** `POST /send-email`

**curl example:**
```bash
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Test Email",
    "body": "<h1>Hello!</h1><p>This is a test email</p>",
    "is_html": true
  }'
```

**Python requests example:**
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    "http://localhost:8000/send-email",
    json={
        "to": ["recipient@example.com"],
        "subject": "Hello from Email Service",
        "body": "<h1>Welcome</h1><p>Email sent via API</p>",
        "is_html": True,
        "cc": ["cc@example.com"],
        "bcc": ["bcc@example.com"]
    },
    auth=HTTPBasicAuth("admin", "changeme")
)

print(response.json())
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-16T10:30:45.123456"
}
```

---

### 3. Send Email with Bearer Token

**Endpoint:** `POST /send-email/token`

**curl example:**
```bash
curl -X POST http://localhost:8000/send-email/token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token-here" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "API Token Email",
    "body": "Email sent with API token",
    "is_html": false
  }'
```

---

### 4. Send SMS with Basic Auth

**Endpoint:** `POST /send-sms`

**curl example:**
```bash
curl -X POST http://localhost:8000/send-sms \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "recipient": "0501234567",
    "text": "Hello from the API",
    "recipient_type": 0
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "SMS sent successfully",
  "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-03-25T10:30:45.123456"
}
```

---

### 5. Send SMS with Bearer Token

**Endpoint:** `POST /send-sms/token`

**curl example:**
```bash
curl -X POST http://localhost:8000/send-sms/token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token-here" \
  -d '{
    "recipient": "0501234567",
    "text": "Token-authenticated SMS",
    "recipient_type": 0
  }'
```

---

### 6. Get API Tokens (Admin Only)

**Endpoint:** `GET /tokens`

Returns all configured API tokens in clear text.  
**Restricted to the `admin` user only** — other Basic Auth users get 403 Forbidden.

```bash
curl -u admin:changeme http://localhost:8000/tokens
```

**Response:**
```json
{
  "tokens": ["my-secure-token-123", "another-secure-token"],
  "count": 2,
  "authenticated_user": "admin"
}
```

---

### 7. Get Service Status (Requires Auth)

**Endpoint:** `GET /status`

```bash
curl http://localhost:8000/status \
  -u "admin:changeme"
```

---

## Request Schemas

### SendEmailRequest

```json
{
  "to": ["recipient1@example.com", "recipient2@example.com"],
  "subject": "Email Subject (max 255 chars)",
  "body": "Email body content (HTML or plain text)",
  "cc": ["optional@example.com"],
  "bcc": ["optional@example.com"],
  "is_html": true
}
```

**Fields:**
- `to` *(required)* — List of recipient email addresses
- `subject` *(required)* — Email subject (1-255 characters)
- `body` *(required)* — Email body content
- `cc` *(optional)* — List of CC recipients
- `bcc` *(optional)* — List of BCC recipients
- `is_html` *(optional, default: true)* — Content type (HTML or plain text)

### SendSmsRequest

```json
{
  "recipient": "0501234567",
  "text": "Your message here",
  "recipient_type": 0
}
```

**Fields:**
- `recipient` *(required)* — Phone number or ID number
- `text` *(required)* — SMS message content
- `recipient_type` *(optional, default: 0)* — 0 = phone number, 1 = ID (Teudat Zehut)

---

## Configuration

Edit `.env` file or environment variables:

```env
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# SMS Configuration
SMS_API_URL=http://your-sms-gateway/sms-api
SMS_CLIENT_ID=your-client-id
SMS_CLIENT_SECRET=your-client-secret
SMS_SCOPE=your-scope
SMS_APP_ID=your-app-id
SMS_SENDER_NAME=YourApp

# Basic Auth Users
BASIC_AUTH_USERS={"admin": "changeme", "user1": "password123"}

# API Tokens
API_TOKENS=["token1", "token2"]
```

### For Different SMTP Providers

**Gmail:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Microsoft 365:**
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

**SendGrid:**
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

---

## Docker Deployment

Build and run:
```bash
docker build -t email-sms-service .
docker run -p 8000:8000 --env-file .env email-sms-service
```

Or use Docker Compose:
```bash
docker-compose up
```

---

## Project Structure

```
email_service/
├── main.py              # FastAPI application & routes
├── config.py            # Configuration & settings
├── auth.py              # Authentication logic (Basic & Bearer)
├── models.py            # Pydantic models for requests/responses
├── email_sender.py      # SMTP email sending logic
├── sms_sender.py        # SMS gateway sending logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Docker Compose config
├── .env                 # Runtime configuration (secrets)
├── .env.example         # Config template
└── instractions/        # Documentation
    ├── README.md
    ├── ARCHITECTURE.md
    ├── PROJECT_SUMMARY.md
    ├── QUICKSTART.md
    └── FRAMEWORK_ANALYSIS.md
```

---

## CORS Configuration

**CORS (Cross-Origin Resource Sharing)** controls which websites/domains are allowed to call this API from a browser. By default the service allows **all origins** (`"*"`), which is fine for development but should be restricted in production.

### Why restrict?
When `allow_origins=["*"]`, any website can make requests to your API from a user's browser. A malicious site could call `/send-email` using a victim's saved credentials.

### How to restrict

In `main.py`, replace `["*"]` with a list of your trusted frontend URLs:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.example.com",
        "https://admin-panel.example.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],           # Only allow needed methods
    allow_headers=["Authorization", "Content-Type"],  # Only allow needed headers
)
```

**Rules:**
- Each origin must include the scheme (`https://`) and domain
- Do **not** include a trailing slash (`https://example.com` ✅, `https://example.com/` ❌)
- Subdomains are separate origins (`app.example.com` ≠ `example.com`)
- For environment-based config, add an `ALLOWED_ORIGINS` list to `config.py` and `.env`:
  ```env
  ALLOWED_ORIGINS=["https://your-frontend.example.com"]
  ```
  Then use `allow_origins=settings.ALLOWED_ORIGINS` in `main.py`.

---
