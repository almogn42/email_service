# Architecture Overview — Email & SMS Service v1.0.6

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   Browser    │    │  Curl/CLI    │    │ Python Code  │     │
│   │   (REST)     │    │  (Shell)     │    │  (Requests)  │     │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│          │                   │                   │               │
│          └───────────────────┼───────────────────┘               │
│                              │                                   │
│                          HTTP/HTTPS                              │
│                              │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER (Port 8000)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MIDDLEWARE LAYER                                        │  │
│  │  ├─ CORS Middleware                                     │  │
│  │  ├─ Logging (RotatingFileHandler + Console)             │  │
│  │  │   └─ Uvicorn access/error logs captured to same     │  │
│  │  │      file (console == file output)                   │  │
│  │  └─ Exception Handlers (HTTP + catch-all)               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ROUTER LAYER                                            │  │
│  │  ├─ GET    /                      ────► Service Info    │  │
│  │  ├─ GET    /health                ────► Health Check    │  │
│  │  ├─ GET    /status                ────► Service Status  │  │
│  │  ├─ POST   /send-email            ────► Email (Basic)  │  │
│  │  ├─ POST   /send-email/token      ────► Email (Token)  │  │
│  │  ├─ POST   /send-sms              ────► SMS (Basic)    │  │
│  │  ├─ POST   /send-sms/token        ────► SMS (Token)    │  │
│  │  ├─ POST   /upload-contacts       ────► Admin Upload   │  │
│  │  ├─ GET    /contacts              ────► Admin View     │  │
│  │  └─ GET    /tokens                ────► Admin Tokens   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  AUTHENTICATION LAYER (auth.py)                          │  │
│  │  ├─ verify_basic_auth()   ◄──── HTTP Basic Header      │  │
│  │  ├─ verify_oauth_token()  ◄──── Bearer Token Header    │  │
│  │  └─ verify_auth()         ◄──── Either Method          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  VALIDATION LAYER (models.py — Pydantic v2)              │  │
│  │  ├─ EmailStr validation                                 │  │
│  │  ├─ Length & type validation                            │  │
│  │  ├─ Required fields                                     │  │
│  │  └─ Mutual exclusion: to/owner, recipient/owner         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  RECIPIENT RESOLUTION LAYER (owner_contacts.py)          │  │
│  │  ├─ resolve_emails(owner)  → deduplicated email list   │  │
│  │  ├─ resolve_phones(owner)  → deduplicated phone list   │  │
│  │  ├─ save_contacts(data)    → overwrite contacts file   │  │
│  │  └─ get_all_contacts()     → full contacts dict        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  BUSINESS LOGIC LAYER (main.py handlers)                 │  │
│  │  ├─ Resolve recipients (direct or via owner groups)     │  │
│  │  ├─ Call email/SMS sender                               │  │
│  │  ├─ Handle multi-recipient SMS (loop + aggregate)       │  │
│  │  └─ Return formatted JSON response                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                    ┌─────────┴─────────┐                      │
│                    ▼                   ▼                      │
│  ┌──────────────────────────┐ ┌──────────────────────────┐  │
│  │ EMAIL SENDING LAYER      │ │ SMS SENDING LAYER        │  │
│  │ (email_sender.py)        │ │ (sms_sender.py)          │  │
│  │                          │ │                          │  │
│  │ SMTPEmailSender [ASYNC]  │ │ SmsSender [ASYNC]        │  │
│  │  ├─ Build MIME message   │ │  ├─ Build auth headers   │  │
│  │  ├─ Resolve TLS mode     │ │  ├─ Build JSON payload   │  │
│  │  ├─ Create SSL context   │ │  ├─ Resolve SSL/verify   │  │
│  │  ├─ Connect + login      │ │  ├─ POST via httpx       │  │
│  │  └─ Send + return result │ │  └─ Return result        │  │
│  └──────────────────────────┘ └──────────────────────────┘  │
│                    │                   │                      │
│                Response (JSON)    Response (JSON)             │
│                    │                   │                      │
└────────────────────┼───────────────────┼─────────────────────┘
                     │                   │
                     ▼                   ▼
         ┌────────────────┐    ┌────────────────┐
         │  SMTP SERVER   │    │  SMS GATEWAY   │
         │  (Gmail, etc)  │    │  (HTTP API)    │
         └────────────────┘    └────────────────┘
                 │                      │
                 ▼                      ▼
         ┌────────────────┐    ┌────────────────┐
         │   Email Body   │    │  SMS Message   │
         │  To Recipients │    │  To Recipient  │
         └────────────────┘    └────────────────┘

```

---

## Data Flow Diagrams

### Email Request Flow (Happy Path)

```
Client Request
      │
      ├─ Authorization Header (Basic Auth or Bearer Token)
      │
      ▼
Authentication Layer (auth.py)
      │
      ├─ Validates credentials ✓
      │
      ├─ Extracts Username/Token
      │
      ▼
Request Body Validation (models.py — Pydantic v2)
      │
      ├─ Validates email addresses (EmailStr) ✓
      ├─ Validates subject length (1–255) ✓
      ├─ Validates body not empty ✓
      ├─ Mutual exclusion: to/owner ✓
      │
      ▼
Recipient Resolution (owner_contacts.py)
      │
      ├─ If "owner" provided → resolve group → email list
      ├─ If "to" provided → use directly
      │
      ▼
Handler Function (main.py)
      │
      ├─ Calls email_sender.send_email()
      │
      ▼
SMTP Operation (email_sender.py — Async)
      │
      ├─ Determine TLS mode (auto/starttls/implicit/none)
      ├─ Create SSL context (verify/custom CA/skip)
      ├─ Connect to SMTP server
      ├─ Login with credentials
      ├─ Send email
      │
      ▼
Success Response
      │
      └─ Returns JSON with message_id & timestamp
```

### SMS Request Flow (Happy Path)

```
Client Request
      │
      ├─ Authorization Header
      │
      ▼
Authentication Layer
      │
      ▼
Request Validation (mutual exclusion: recipient/owner)
      │
      ▼
Recipient Resolution
      │
      ├─ If "owner" → resolve group → phone list
      ├─ If "recipient" → single phone
      │
      ▼
Handler (main.py) — Loop over recipients
      │
      ├─ For each recipient:
      │   └─ sms_sender.send_sms()
      │       ├─ Build auth headers (x-client-id, x-client-secret, x-scope)
      │       ├─ Build JSON payload
      │       ├─ POST to SMS gateway via httpx
      │       └─ Return result
      │
      ▼
Aggregated Response
      │
      └─ "SMS sent successfully to N/M recipients"
```

---

### Error Handling Flow

```
Request arrives
      │
      ▼
     Check Authentication
      │
      ├─ NO auth header  ──► 401 Unauthorized
      │
      ├─ Invalid creds   ──► 401 Invalid credentials
      │
      ▼
     Validate Request Body
      │
      ├─ Invalid email   ──► 422 Invalid email format
      ├─ Missing field   ──► 422 Missing required field
      ├─ Wrong type      ──► 422 Type validation error
      ├─ Both to+owner   ──► 422 Mutual exclusion error
      ├─ Neither to/owner──► 422 Must provide one
      │
      ▼
     Resolve Recipients
      │
      ├─ Unknown group   ──► 400 Owner group not found
      ├─ No contacts     ──► 400 No emails/phones found
      │
      ▼
     Execute Send
      │
      ├─ SMTP auth fail  ──► 500 SMTP authentication failed
      ├─ SMTP connect    ──► 500 SMTP connect error
      ├─ SMS gateway err ──► 500 SMS API error
      ├─ SSL error       ──► 500 SSL certificate error
      │
      └─ Success         ──► 200 Sent successfully
```

---

## Component Interaction

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                    │
│  CONFIGURATION (config.py)                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ • SMTP settings (server, port, TLS mode, SSL verify/CA)    │  │
│  │ • SMS gateway settings (URL, credentials, SSL verify/CA)   │  │
│  │ • Basic auth users (auto-hashed passwords)                 │  │
│  │ • API tokens                                               │  │
│  │ • Service name, debug mode, log level                      │  │
│  └────────────────────────────────────────────────────────────┘  │
│           ▲                                ▲                      │
│           │                                │                      │
│           └────────────────────┬───────────┘                      │
│                                │                                  │
│                   Used by all components                          │
│                                │                                  │
│     ┌─────────────┬───────────┼───────────┬─────────────┐       │
│     │             │           │           │             │       │
│     ▼             ▼           ▼           ▼             ▼       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐│
│  │ auth.py  │ │ main.py  │ │email_    │ │sms_      │ │owner_ ││
│  │          │ │          │ │sender.py │ │sender.py │ │contact││
│  │Validates │ │Routes &  │ │          │ │          │ │s.py   ││
│  │username/ │◄►│Handlers  │►│Sends     │ │Sends     │ │       ││
│  │password  │ │          │ │emails    │ │SMS msgs  │ │Resolves│
│  │& tokens  │ │          │ │via SMTP  │ │via HTTP  │ │groups  ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────┘│
│                    │                                             │
│                    ▼                                             │
│              ┌──────────────┐                                    │
│              │  models.py   │                                    │
│              │              │                                    │
│              │• SendEmail   │                                    │
│              │  Request     │                                    │
│              │• SendSms     │                                    │
│              │  Request     │                                    │
│              │• Upload      │                                    │
│              │  Contacts    │                                    │
│              │• Responses   │                                    │
│              │• ServiceStat │                                    │
│              └──────────────┘                                    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Development
```
Client
  ▲
  │ HTTP (localhost:8000)
  ▼
Uvicorn Server (Development, reload=True when DEBUG=True)
  │
  ├─ main.py (FastAPI app)
  ├─ Logs → console + logs/app.log (rotating, 5 MB × 5 backups)
  │          ↑ includes Uvicorn access & error logs
  │            (uvicorn, uvicorn.error, uvicorn.access loggers all share
  │             the same RotatingFileHandler — console and file are identical)
  │
  ├─ SMTP Server Connection
  └─ SMS Gateway Connection
```

### Production (Docker)
```
┌─────────────────────────────┐
│   Docker Container          │
│  ┌───────────────────────┐  │
│  │ Uvicorn Server        │  │
│  │ (Port 8000)           │  │
│  ├───────────────────────┤  │
│  │ Email & SMS Service   │  │
│  │ • main.py             │  │
│  │ • config.py           │  │
│  │ • auth.py             │  │
│  │ • models.py           │  │
│  │ • email_sender.py     │  │
│  │ • sms_sender.py       │  │
│  │ • owner_contacts.py   │  │
│  │ • data/contacts.json  │  │
│  └───────────────────────┘  │
│  Volumes:                   │
│  • ./logs → /app/logs       │
│  • (optional) cert.pem      │
└─────────────────────────────┘
  ▲                    │         │
  │                    │         │
HTTP/HTTPS        SMTP/TLS    HTTP(S)
(Reverse Proxy)   (Gmail/etc) (SMS GW)
  │                    │         │
  ▼                    ▼         ▼
Load Balancer    Email Provider  SMS Gateway
```

### High-Availability (Production Grade)
```
┌──────────────┐
│   Clients    │
└──────┬───────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────┐
│   Nginx Reverse Proxy       │
│   (Load Balancer)           │
└────┬────────────────────┬───┘
     │                    │
     ▼                    ▼
┌─────────────────┐ ┌─────────────────┐
│ Email Service 1 │ │ Email Service 2 │ ...
│   (Docker)      │ │   (Docker)      │
└────────┬────────┘ └────────┬────────┘
         │                   │
         └────────┬──────────┘
                  │
          ┌───────┴───────┐
          │               │
          ▼               ▼
  ┌───────────────┐ ┌──────────┐
  │ SMTP Provider │ │ SMS GW   │
  │ (Gmail, etc)  │ │ (HTTP)   │
  └───────────────┘ └──────────┘

Optional Components:
├─ Redis: Rate limiting, caching
├─ PostgreSQL: Email history logs
├─ Prometheus: Metrics collection
├─ ELK Stack: Centralized logging
└─ Sentry: Error tracking
```

---

## Sequence Diagram: Send Email Request

```
Client              FastAPI        Auth        Models     Contacts     Email        SMTP
  │                   │             │            │          Module      Sender       Server
  │                   │             │            │            │           │           │
  ├─ POST /send-    ─►├─ Receive    │            │            │           │           │
  │  email (Auth)     │  request    │            │            │           │           │
  │                   │             │            │            │           │           │
  │                   ├─ Extract  ──►├─ Validate │            │           │           │
  │                   │  auth       │ creds     │            │           │           │
  │                   │◄─ Return ───┤ ✓ OK      │            │           │           │
  │                   │  user       │           │            │           │           │
  │                   │             │           │            │           │           │
  │                   ├─ Parse body ────────────►├─ Validate │           │           │
  │                   │              │           │ to/owner  │           │           │
  │                   │              │           │ & schema  │           │           │
  │                   │              │◄──────────┤ ✓ Valid   │           │           │
  │                   │              │           │           │           │           │
  │                   ├─ Resolve recipients ─────────────────►│           │           │
  │                   │  (if owner was given)    │           │           │           │
  │                   │◄─ Return email list ─────────────────┤           │           │
  │                   │                          │           │           │           │
  │                   ├─ Call ────────────────────────────────────────────►│           │
  │                   │ send_email()             │           │           │           │
  │                   │                          │           │           │           │
  │                   │                          │           │           ├─ TLS ─────►
  │                   │                          │           │           │ Connect   │
  │                   │                          │           │           │           │
  │                   │                          │           │           ├─ Login ───►
  │                   │                          │           │           │           │
  │                   │                          │           │           ├─ Send ────►
  │                   │                          │           │           │ Email     │
  │                   │                          │           │           │◄── OK ────┤
  │                   │                          │           │           │           │
  │                   │◄────────── Return ───────┤◄──────────┤◄──────────┤           │
  │                   │ {success: true,          │           │           │           │
  │                   │  message_id: xxx}        │           │           │           │
  │                   │                          │           │           │           │
  │◄─ 200 OK ─────────┤                          │           │           │           │
  │  + JSON response  │                          │           │           │           │
  │                   │                          │           │           │           │
```

---

## File Dependencies

```
main.py
  ├─ Imports: config, auth, models, email_sender, sms_sender, owner_contacts
  │
config.py
  ├─ Imports: auth (inside field_validator, to avoid circular import)
  │
auth.py
  ├─ Imports: config (mid-file, after hashing utils, to avoid circular import)
  │
models.py
  ├─ Standalone (Pydantic only)
  │
email_sender.py
  ├─ Imports: config
  │
sms_sender.py
  ├─ Imports: config
  │
owner_contacts.py
  ├─ Standalone (json, os, logging only)
  │
examples.py (Tests_and_examples/)
  ├─ External: requests library only
  │
test_email_service.py (Tests_and_examples/)
  ├─ Imports: main (for TestClient)

Dependency Graph:
─────────────────
main.py
  ├─► config.py ◄──┐
  ├─► auth.py ──────┤ (circular — resolved via delayed import)
  ├─► models.py     │
  ├─► email_sender.py ──► config.py
  ├─► sms_sender.py ────► config.py
  └─► owner_contacts.py  (standalone — reads data/contacts.json)
```

---

## Technology Stack

```
┌─────────────────────────────────────────┐
│          TECHNOLOGY STACK               │
├─────────────────────────────────────────┤
│                                         │
│  Backend Framework                      │
│  └─ FastAPI 0.104                       │
│     └─ Starlette (async)                │
│                                         │
│  ASGI Server                            │
│  └─ Uvicorn 0.24                        │
│                                         │
│  Data Validation                        │
│  └─ Pydantic 2.5 + pydantic-settings    │
│     └─ Email Validator 2.1              │
│                                         │
│  SMTP Integration                       │
│  └─ aiosmtplib 3.0 (async)              │
│                                         │
│  HTTP Client (SMS Gateway)              │
│  └─ httpx 0.25 (async)                  │
│                                         │
│  Authentication                         │
│  ├─ HTTP Basic Auth (built-in)          │
│  ├─ Bearer Tokens (manual)              │
│  ├─ python-jose 3.3 (JWT ready)         │
│  └─ passlib 1.7 (PBKDF2-SHA256)         │
│                                         │
│  Async/Concurrency                      │
│  └─ Python asyncio                      │
│                                         │
│  Testing                                │
│  ├─ pytest 7.4                          │
│  ├─ pytest-asyncio 0.21                 │
│  └─ httpx 0.25 (async HTTP client)      │
│                                         │
│  Containerization                       │
│  ├─ Docker (python:3.11-slim)           │
│  └─ Docker Compose 3.8                  │
│                                         │
│  Programming Language                   │
│  └─ Python 3.11                         │
│                                         │
└─────────────────────────────────────────┘
```

---

## Key Design Patterns

### 1. Dependency Injection (FastAPI)
```python
@app.post("/send-email")
async def send_email(
    request: SendEmailRequest,
    username: str = Depends(verify_basic_auth)
):
    # username is automatically injected after auth verification
    pass
```

### 2. Async/Await (Non-blocking I/O)
```python
async def send_email(self, ...):
    async with aiosmtplib.SMTP(...) as smtp:
        await smtp.login(...)
        await smtp.sendmail(...)
```

### 3. Singleton Pattern (Email & SMS Senders)
```python
# email_sender.py
email_sender = SMTPEmailSender()  # Single instance per process

# sms_sender.py
sms_sender = SmsSender()          # Single instance per process
```

### 4. Configuration Management (Cached Settings)
```python
@lru_cache()
def get_settings():
    return Settings()  # Created once, reused everywhere
```

### 5. Mutual Exclusion Validation (Pydantic model_validator)
```python
@model_validator(mode="after")
def check_exactly_one_recipient_source(self):
    # Ensures exactly one of 'to'/'owner' is provided
    # Raises ValueError if both or neither are given
```

### 6. Auto-Hashing (Password Security)
```python
@field_validator('BASIC_AUTH_USERS')
def hash_passwords(cls, users_dict):
    # Hashes plain-text passwords on first startup
    # Persists hashed values back to .env
```

---
