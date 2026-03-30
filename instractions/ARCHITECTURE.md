# Architecture Overview — Email & SMS Service

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
│  │  ├─ Logging Middleware                                  │  │
│  │  └─ Exception Handlers                                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ROUTER LAYER                                            │  │
│  │  ├─ GET    /health                ────► Health Check    │  │
│  │  ├─ GET    /                      ────► Service Info    │  │
│  │  ├─ GET    /status                ────► Service Status  │  │
│  │  ├─ POST   /send-email            ────► Email (Basic)  │  │
│  │  ├─ POST   /send-email/token      ────► Email (Token)  │  │
│  │  ├─ POST   /send-sms              ────► SMS (Basic)    │  │
│  │  ├─ POST   /send-sms/token        ────► SMS (Token)    │  │
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
│  │  VALIDATION LAYER (models.py - Pydantic)                │  │
│  │  ├─ EmailStr validation                                 │  │
│  │  ├─ Length validation                                   │  │
│  │  ├─ Type checking                                       │  │
│  │  └─ Required fields                                     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  BUSINESS LOGIC LAYER (main.py handlers)                 │  │
│  │  ├─ Extract request data                                │  │
│  │  ├─ Call email sender                                   │  │
│  │  ├─ Handle response                                     │  │
│  │  └─ Return formatted JSON                               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  EMAIL SENDING LAYER (email_sender.py)                   │ │
│  │  ┌─────────────────────────────────────────┐             │ │
│  │  │ SMTPEmailSender.send_email() [ASYNC]   │             │ │
│  │  │  ├─ Build MIMEMessage                  │             │ │
│  │  │  ├─ Collect recipients                 │             │ │
│  │  │  ├─ Connect to SMTP                    │             │ │
│  │  │  ├─ Login with credentials             │             │ │
│  │  │  ├─ Send message                       │             │ │
│  │  │  └─ Return result                      │             │ │
│  │  └─────────────────────────────────────────┘             │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  SMS SENDING LAYER (sms_sender.py)                       │ │
│  │  ┌─────────────────────────────────────────┐             │ │
│  │  │ SmsSender.send_sms() [ASYNC]           │             │ │
│  │  │  ├─ Build auth headers                 │             │ │
│  │  │  ├─ Format payload from template       │             │ │
│  │  │  ├─ POST to SMS gateway via httpx      │             │ │
│  │  │  └─ Return result                      │             │ │
│  │  └─────────────────────────────────────────┘             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                          Response (JSON)                        │
│                              │                                  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
        ┌────────────────┐              ┌────────────────┐
        │  SMTP SERVER   │              │  SMS GATEWAY   │
        │  (Gmail, etc)  │              │  (HTTP API)    │
        └────────────────┘              └────────────────┘
                │                                │
                ▼                                ▼
        ┌────────────────┐              ┌────────────────┐
        │   Email Body   │              │  SMS Message   │
        │   To Recipients│              │  To Recipient  │
        └────────────────┘              └────────────────┘

```

---

## Data Flow Diagrams

### Request Flow (Happy Path)

```
Client Request
      │
      ├─ Authorization Header (Basic Auth or Bearer Token)
      │
      ▼
Authentication Layer
      │
      ├─ Validates credentials ✓
      │
      ├─ Extracts Username/Token
      │
      ▼
Request Body Validation (Pydantic)
      │
      ├─ Validates email addresses ✓
      │
      ├─ Validates subject length ✓
      │
      ├─ Validates body not empty ✓
      │
      ▼
Handler Function (Business Logic)
      │
      ├─ Calls email_sender.send_email()
      │
      ▼
SMTP Operation (Async)
      │
      ├─ Connects to SMTP server
      │
      ├─ Sends authentication
      │
      ├─ Sends email
      │
      ▼
Success Response
      │
      └─ Returns JSON with message_id
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
      │
      ├─ Missing field   ──► 422 Missing required field
      │
      ├─ Wrong type      ──► 422 Type validation error
      │
      ▼
     Execute Email Send
      │
      ├─ SMTP failed     ──► 500 SMTP error message
      │
      ├─ Auth failed     ──► 500 Authentication failed
      │
      └─ Success         ──► 200 Email sent
```

---

## Component Interaction

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                    │
│  CONFIGURATION (config.py)                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ • SMTP settings                                            │  │
│  │ • Basic auth users                                         │  │
│  │ • API tokens                                               │  │
│  │ • Security settings                                        │  │
│  └────────────────────────────────────────────────────────────┘  │
│           ▲                                ▲                      │
│           │                                │                      │
│           └────────────────────┬───────────┘                      │
│                                │                                  │
│                   Used by all components                          │
│                                │                                  │
│     ┌──────────────────────────┼──────────────────────────┐      │
│     │                          │                          │      │
│     ▼                          ▼                          ▼      │
│  ┌──────────┐              ┌──────────┐             ┌──────────┐│
│  │  auth.py │              │ main.py  │             │email_    ││
│  │          │              │          │             │sender.py ││
│  │Validates │              │Routes &  │             │          ││
│  │username/ │◄────────────►│Handlers  │◄───────────►│Sends     ││
│  │password  │              │          │             │emails    ││
│  │& tokens  │              │          │             │          ││
│  └──────────┘              └──────────┘             └──────────┘│
│                                │                                  │
│                    ┌───────────┴───────────┐                    │
│                    │                       │                    │
│                    ▼                       ▼                    │
│              ┌──────────────┐        ┌──────────────┐           │
│              │  models.py   │        │  config.py   │           │
│              │              │        │              │           │
│              │• SendEmail   │        │• Settings    │           │
│              │  Request     │        │  Instance    │           │
│              │• SendEmail   │        │• Cached conf │           │
│              │  Response    │        │              │           │
│              └──────────────┘        └──────────────┘           │
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
Uvicorn Server (Development)
  │
  ├─ main.py (FastAPI app)
  │
  └─ SMTP Server Connection
```

### Production (Docker)
```
┌─────────────────────────────┐
│   Docker Container          │
│  ┌───────────────────────┐  │
│  │ Uvicorn Server        │  │
│  │ (Port 8000)           │  │
│  ├───────────────────────┤  │
│  │ Email Service App     │  │
│  │ • main.py             │  │
│  │ • config.py           │  │
│  │ • auth.py             │  │
│  │ • email_sender.py     │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
  ▲                        │
  │                        │
HTTP/HTTPS             SMTP/TLS
(Reverse Proxy)        (Gmail/etc)
  │                        │
  ▼                        ▼
Load Balancer          Email Provider
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
                  │ SMTP/TLS
                  ▼
          ┌───────────────┐
          │ SMTP Provider │
          │ (Gmail, etc)  │
          └───────────────┘

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
Client              FastAPI        Auth        Models      Email        SMTP
  │                   │             │            │          Sender       Server
  │                   │             │            │            │           │
  ├─ POST /send-    ─►├─ Receive    │            │            │           │
  │  email (Auth)     │  request    │            │            │           │
  │                   │             │            │            │           │
  │                   ├─ Extract  ──►├─ Validate │            │           │
  │                   │  auth       │ creds     │            │           │
  │                   │◄─ Return ───┤ ✓ OK      │            │           │
  │                   │  user       │           │            │           │
  │                   │             │           │            │           │
  │                   ├─ Parse body ────────────►├─ Validate │           │
  │                   │              │           │ email fmt │           │
  │                   │              │           │ & schema  │           │
  │                   │              │◄──────────┤ ✓ Valid   │           │
  │                   │              │           │           │           │
  │                   ├─ Call ───────────────────┼─────────────►         │
  │                   │ send_email()             │           │           │
  │                   │                          │           │           │
  │                   │                          │           ├─ Connect ─►
  │                   │                          │           │ to SMTP  │
  │                   │                          │           │           │
  │                   │                          │           Authenticated
  │                   │                          │           │           │
  │                   │                          │           ├─ Send ───►
  │                   │                          │           │ Email    │
  │                   │                          │           │◄┤ OK      │
  │                   │                          │           │           │
  │                   │◄────────── Return ───────┤◄──────────┤           │
  │                   │ {success: true,          │           │           │
  │                   │  message_id: xxx}        │           │           │
  │                   │                          │           │           │
  │◄─ 200 OK ─────────┤                          │           │           │
  │  + JSON response  │                          │           │           │
  │                   │                          │           │           │
```

---

## File Dependencies

```
main.py
  ├─ Imports: config, auth, models, email_sender, sms_sender
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
examples.py
  ├─ External: requests library only
  │
test_email_service.py
  ├─ Imports: main (for TestClient)

Dependency Graph:
─────────────────
main.py
  ├─► config.py
  ├─► auth.py ──► config.py
  ├─► models.py
  ├─► email_sender.py ──► config.py
  └─► sms_sender.py ──► config.py
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
│  └─ Pydantic 2.5                        │
│     └─ Email Validator                  │
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
│  └─ passlib 1.7 (password hashing)      │
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
│  ├─ Docker                              │
│  └─ Docker Compose                      │
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

### 3. Singleton Pattern (Email Sender)
```python
email_sender = SMTPEmailSender()  # Single instance
```

### 4. Configuration Management
```python
settings = get_settings()  # Cached settings instance
```

---

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple FastAPI instances
- Use load balancer (Nginx, HAProxy)
- Stateless design (no session data)

### Vertical Scaling
- Increase SMTP connection pool
- Optimize async workers
- Use production ASGI server (Gunicorn + Uvicorn)

### Database Addition
- PostgreSQL for email history
- Redis for rate limiting
- Cache SMTP connections

### Monitoring
- Prometheus metrics endpoints
- Centralized logging (ELK, CloudWatch)
- Error tracking (Sentry, Rollbar)
