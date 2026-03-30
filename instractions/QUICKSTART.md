# Quick Start Guide for Email & SMS Service

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Configure SMTP

### Option A: Gmail (Recommended for Testing)
1. Enable 2-Factor Authentication on your Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy your 16-character app password
4. Update `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

### Option B: Other Email Providers
- **Outlook/Office 365**: smtp.office365.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **SendGrid**: smtp.sendgrid.net:587 (username: "apikey")
- **Custom SMTP**: Use your provider's settings

## Step 3: Configure SMS Gateway

Edit `.env` with your SMS gateway credentials:
```
SMS_API_URL=http://your-gateway/sms-api
SMS_CLIENT_ID=your-client-id
SMS_CLIENT_SECRET=your-client-secret
SMS_SCOPE=your-scope
SMS_APP_ID=your-app-id
SMS_SENDER_NAME=YourApp
```

## Step 4: Configure Authentication

Edit `.env` to set your credentials:
```
BASIC_AUTH_USERS={"admin": "changeme", "user1": "mypassword"}
API_TOKENS=["my-secure-token-123", "another-token"]
```

> **Note:** Plain-text passwords in `BASIC_AUTH_USERS` are automatically hashed (PBKDF2-SHA256) on first startup and persisted back to `.env`.

## Step 5: Start the Service
```bash
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Step 6: Test the Service

### Option A: Using Browser (Swagger UI)
Visit: http://localhost:8000/docs

### Option B: Using curl

**Health check (no auth):**
```bash
curl http://localhost:8000/health
```

**Send Email (Basic Auth):**
```bash
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "to": ["your-email@gmail.com"],
    "subject": "Test Email",
    "body": "<h1>Success!</h1><p>Your email service works!</p>",
    "is_html": true
  }'
```

**Send SMS (Basic Auth):**
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

**Send Email (Bearer Token):**
```bash
curl -X POST http://localhost:8000/send-email/token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-secure-token-123" \
  -d '{
    "to": ["your-email@gmail.com"],
    "subject": "Token Auth Test",
    "body": "Email sent with token auth",
    "is_html": false
  }'
```

**View API Tokens (admin only):**
```bash
curl -u admin:changeme http://localhost:8000/tokens
```

## Step 7: Explore API Documentation

- **Swagger UI**: http://localhost:8000/docs (interactive testing)
- **ReDoc**: http://localhost:8000/redoc (read-only docs)

## Troubleshooting

### SSL/TLS Certificate Verification Errors
- If connecting to an internal/organization SMTP server with a custom or self-signed certificate, you may get an `[SSL: CERTIFICATE_VERIFY_FAILED]` error.
- **Fix 1 (Preferred):** Provide the path to your organization's CA certificate in `.env` using `SMTP_CA_CERT_PATH=/path/to/cert.pem`
- **Fix 2 (Testing):** Set `SMTP_SSL_VERIFY=False` in your `.env` to ignore certificate errors.

### "SMTP Authentication failed"
- Verify credentials in `.env`
- For Gmail: Use app password, not regular password
- Ensure 2FA is enabled on Gmail account

### Connection refused
- Make sure service is running with `python main.py`
- Check port 8000 is not blocked
- Verify SMTP server settings

### SMS sending fails
- Verify SMS_API_URL is reachable
- Check gateway credentials (SMS_CLIENT_ID, SMS_CLIENT_SECRET)
- Inspect gateway logs for error details

## File Structure

```
email_service/
├── main.py           # FastAPI app — START HERE
├── config.py         # Configuration & settings
├── auth.py           # Authentication logic
├── models.py         # Data models
├── email_sender.py   # SMTP email logic
├── sms_sender.py     # SMS gateway logic
├── requirements.txt  # Dependencies
├── Dockerfile        # Container definition
├── docker-compose.yml# Docker Compose config
├── .env.example      # Config template
├── .env              # Your config (created from .env.example)
└── instractions/     # Documentation
```

## Support

For detailed API documentation, see `README.md`  
For code examples, see `Tests_and_examples/examples.py`
