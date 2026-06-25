# Email & SMS Service API

A FastAPI-based microservice for sending **emails** and **SMS messages** via web requests with support for **Basic Authentication** and **Bearer Token (OAuth) Authentication**.

**Current Version:** `1.0.6`

## Features

✅ **Dual Authentication Methods**
- HTTP Basic Authentication (username/password)
- Bearer Token Authentication (API key)

✅ **SMTP Email Sending**
- Support for HTML and plain text emails
- CC and BCC recipients
- Async SMTP for high performance
- Configurable TLS mode (`starttls`, `implicit`, `none`, `auto`)
- Support for custom CA SSL certificates & bypassing validation for internal networks

✅ **SMS Sending**
- External SMS gateway integration via HTTP
- Configurable payload with OAuth-style headers
- Support for phone-number and ID-based recipients
- Custom SSL CA & verification bypass for SMS gateway

✅ **Owner Contacts System**
- Define named contact groups (e.g. `it_team`, `dev_team`) in a JSON file
- Send email/SMS to group names instead of hardcoded addresses
- Admin endpoints to upload and view contacts
- Supports sending to multiple groups at once (deduplicated)

✅ **Admin Endpoints**
- `GET /tokens` — view all API tokens (admin-only, Basic Auth)
- `POST /upload-contacts` — upload/overwrite owner contact list (admin-only)
- `GET /contacts` — retrieve current owner contact list (admin-only)

✅ **Auto-Generated API Documentation**
- Swagger UI at `/docs`
- ReDoc at `/redoc`

✅ **Production Ready**
- Comprehensive error handling
- Structured logging with rotating file handler
- CORS support
- Input validation with Pydantic
- Password hashing (PBKDF2-SHA256)
- Docker & Docker Compose support

---

## Installation

### 1. Clone or navigate to project directory
```bash
cd email_service/Code
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
cp ../Tests_and_examples/.env.example .env

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

**Using direct recipients:**
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

**Using owner group:**
```bash
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "owner": "it_team",
    "subject": "Team Alert",
    "body": "<h1>Alert</h1><p>Sent to all it_team contacts</p>",
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

**Using direct recipient:**
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

**Using owner group (sends to all phones in the group):**
```bash
curl -X POST http://localhost:8000/send-sms \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "owner": "it_team",
    "text": "Alert for IT team",
    "recipient_type": 0
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "SMS sent successfully to 3/3 recipients",
  "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-03-25T10:30:45.123456"
}
```

---

### 5. Send SMS with Bearer Token

**Endpoint:** `POST /send-sms/token`

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

### 6. Upload Contacts (Admin Only)

**Endpoint:** `POST /upload-contacts`

Upload or overwrite the owner contacts JSON file. Restricted to the `admin` user only.

```bash
curl -X POST http://localhost:8000/upload-contacts \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "Owners": {
      "it_team": {
        "almog": {
          "email": "almog@example.com",
          "phone_number": "0501234567"
        },
        "dana": {
          "email": "dana@example.com",
          "phone_number": "0509876543"
        }
      },
      "dev_team": {
        "yosi": {
          "email": "yosi@example.com",
          "phone_number": "0521111111"
        }
      }
    }
  }'
```

**Response:**
```json
{
  "message": "Contacts saved successfully"
}
```

---

### 7. Get Contacts (Admin Only)

**Endpoint:** `GET /contacts`

Retrieve the current owner contacts list. Restricted to the `admin` user only.

```bash
curl -u admin:changeme http://localhost:8000/contacts
```

---

### 8. Get API Tokens (Admin Only)

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

### 9. Get Service Status (Requires Auth)

**Endpoint:** `GET /status`

```bash
curl http://localhost:8000/status \
  -u "admin:changeme"
```

---

## Request Schemas

### SendEmailRequest

You must provide **exactly one** of `to` (direct email list) **or** `owner` (group name). Providing both or neither returns `422`.

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

**or using owner groups:**

```json
{
  "owner": "it_team",
  "subject": "Email Subject",
  "body": "Email body content",
  "is_html": true
}
```

**Fields:**
- `to` *(optional)* — List of recipient email addresses (mutually exclusive with `owner`)
- `owner` *(optional)* — Owner group name (string) or list of group names to resolve recipients from the contacts file (mutually exclusive with `to`)
- `subject` *(required)* — Email subject (1–255 characters)
- `body` *(required)* — Email body content
- `cc` *(optional)* — List of CC recipients
- `bcc` *(optional)* — List of BCC recipients
- `is_html` *(optional, default: true)* — Content type (HTML or plain text)

### SendSmsRequest

You must provide **exactly one** of `recipient` (direct phone/ID) **or** `owner` (group name). Providing both or neither returns `422`.

```json
{
  "recipient": "0501234567",
  "text": "Your message here",
  "recipient_type": 0
}
```

**or using owner groups:**

```json
{
  "owner": ["it_team", "dev_team"],
  "text": "Alert message",
  "recipient_type": 0
}
```

**Fields:**
- `recipient` *(optional)* — Phone number or ID number (mutually exclusive with `owner`)
- `owner` *(optional)* — Owner group name or list of group names (mutually exclusive with `recipient`)
- `text` *(required)* — SMS message content
- `recipient_type` *(optional, default: 0)* — 0 = phone number, 1 = ID (Teudat Zehut)

### UploadContactsRequest

```json
{
  "Owners": {
    "<group_name>": {
      "<contact_name>": {
        "email": "contact@example.com",
        "phone_number": "0501234567"
      }
    }
  }
}
```

---

## Configuration

Edit `.env` file or environment variables:

```env
# ── General Service Settings ───────────────────────────────────
SERVICE_NAME=Email Service
DEBUG=False
LOG_LEVEL=info                              # Options: info, error, debug

# ── SMTP (Email) Settings ──────────────────────────────────────
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS_MODE=auto                          # Options: starttls, implicit, none, auto
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# ── SMTP SSL / Verification Settings ──────────────────────────
SMTP_SSL_VERIFY=True                        # Set False to bypass SSL validation
SMTP_CA_CERT_PATH=                          # Path to custom .pem/.crt CA file

# ── SMS Gateway Settings ──────────────────────────────────────
SMS_API_URL=http://your-sms-gateway/sms-api
SMS_CLIENT_ID=your-client-id
SMS_CLIENT_SECRET=your-client-secret
SMS_SCOPE=your-scope
SMS_APP_ID=your-app-id
SMS_SENDER_NAME=YourApp

# ── SMS SSL / Verification Settings ───────────────────────────
SMS_SSL_VERIFY=True                         # Set False to bypass SSL for SMS gateway
SMS_CA_CERT_PATH=                           # Path to custom CA for SMS gateway

# ── Basic Auth Users ──────────────────────────────────────────
BASIC_AUTH_USERS={"admin": "changeme", "user1": "password123"}

# ── API Tokens ────────────────────────────────────────────────
API_TOKENS=["token1", "token2"]
```

### SMTP TLS Modes

| Mode | Port | Description |
|------|------|-------------|
| `auto` | any | Auto-detects based on port (587→starttls, 465→implicit, 25→none) |
| `starttls` | 587 | Upgrades plain connection to encrypted via STARTTLS |
| `implicit` | 465 | Connects with SSL/TLS from the start |
| `none` | 25 | Plain text, no encryption (not recommended) |

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

### Option A: Building from scratch
Build and run:
```bash
docker build -t email-sms-service .
docker run -p 8000:8000 --env-file .env email-sms-service
```

### Option B: Running from a compiled image tarball
If you have a pre-built image tarball in `Compiled image/`, you can load and run it without building:

1. Load the image into Docker:
```bash
docker load -i "Compiled image/<image-file>.tar"
```

2. Run the container (make sure your `.env` file is ready):
```bash
docker run -d \
  --name email-sms-service \
  -p 8000:8000 \
  --env-file .env \
  -v ./logs:/app/logs \
  email-sms-service
```
> **Custom SSL Certificates**: If using a custom CA file (`SMTP_CA_CERT_PATH`), mount the certificate into the container:
> `docker run -p 8000:8000 --env-file .env -v /local/path/to/cert.pem:/app/cert.pem email-sms-service` and set `SMTP_CA_CERT_PATH=/app/cert.pem` in `.env`.

Or use Docker Compose:
```bash
docker-compose up
```
> **Note**: If using Docker Compose with custom SSL, uncomment the certificate volume mount in `docker-compose.yml`.

---

## Project Structure

```
email_service/
├── Code/                     # Application source code
│   ├── main.py               # FastAPI application & routes (entry point)
│   ├── config.py             # Configuration & settings (Pydantic)
│   ├── auth.py               # Authentication logic (Basic & Bearer)
│   ├── models.py             # Pydantic request/response models
│   ├── email_sender.py       # Async SMTP email sending logic
│   ├── sms_sender.py         # Async SMS gateway sending logic
│   ├── owner_contacts.py     # Owner contact groups registry
│   ├── data/
│   │   └── contacts.json     # Owner contacts data file
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Container definition
│   ├── docker-compose.yml    # Docker Compose config
│   ├── .env                  # Runtime configuration (secrets — not committed)
│   ├── CHANGELOG.md          # Version history & change notes
│   └── logs/                 # Rotating log files (app.log, auto-created)
├── Tests_and_examples/       # Tests & usage examples
│   ├── examples.py           # Python usage examples
│   ├── test_email_service.py # Pytest unit tests
│   ├── docker-compose.yaml   # Compose file for running tests
│   └── .env.example          # Config template (copy to Code/.env to start)
├── Compiled image/           # Pre-built Docker image tarballs (v1.0.2)
│   ├── email-sms-service_1.0.2_image.tar
│   └── email-sms-service_1.0.2_image.zip
├── test server_sms/          # Local test SMS server for development
├── instractions/             # Documentation
│   ├── ARCHITECTURE.md       # System architecture & design
│   └── QUICKSTART.md         # Getting started guide
└── README.md                 # This file
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
