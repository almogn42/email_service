# Quick Start Guide for Email & SMS Service v1.0.6

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

Copy the example configuration file:
```bash
cp ../Tests_and_examples/.env.example .env
```

### SMTP Configuration
Edit `.env` with your SMTP settings:

**Option A: Gmail (Recommended for Testing)**
1. Enable 2-Factor Authentication on your Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy your 16-character app password
4. Update `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS_MODE=auto
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Option B: Other Email Providers**
- **Outlook/Office 365**: smtp.office365.com:587
- **SendGrid**: smtp.sendgrid.net:587 (username: "apikey")

### SMS Gateway Configuration
Edit `.env` with your SMS gateway credentials:
```env
SMS_API_URL=http://your-gateway/sms-api
SMS_CLIENT_ID=your-client-id
SMS_CLIENT_SECRET=your-client-secret
SMS_SCOPE=your-scope
SMS_APP_ID=your-app-id
SMS_SENDER_NAME=YourApp
```

### Authentication Configuration
Edit `.env` to set your credentials:
```env
BASIC_AUTH_USERS={"admin": "changeme", "user1": "mypassword"}
API_TOKENS=["my-secure-token-123", "another-token"]
```
> **Note:** Plain-text passwords in `BASIC_AUTH_USERS` are automatically hashed (PBKDF2-SHA256) on first startup and persisted back to `.env`.

### Service Settings
Edit `.env` for general settings:
```env
SERVICE_NAME="My Email Service"
DEBUG=False
LOG_LEVEL=info
```

## Step 3: Owner Contacts (Optional)
If you want to send messages to groups (e.g., `it_team`) instead of direct addresses/phones, you need to populate the contacts registry.

You can upload contacts using the admin API after starting the server (see Step 5), or manually create `Code/data/contacts.json`.

## Step 4: Start the Service

### Option A: Using Python directly
```bash
cd Code
python main.py
```
Expected output will show `Uvicorn running on http://0.0.0.0:8000`. All logs (including Uvicorn access logs) are written to `logs/app.log` and also printed to the console.

### Option B: Using Docker
If you have a compiled image tarball in `Compiled image/`:
1. Load the image into Docker:
```bash
docker load -i "Compiled image/<image-file>.tar"
```
2. Run the container:
```bash
docker run -d \
  --name email-sms-service \
  -p 8000:8000 \
  --env-file .env \
  -v ./logs:/app/logs \
  email-sms-service
```
To build the latest source and run it via Docker:
```bash
cd Code
docker build -t email-sms-service .
docker run -d --name email-sms-service -p 8000:8000 --env-file .env -v ./logs:/app/logs email-sms-service
```

## Step 5: Test the Service

### Option A: Using Browser (Swagger UI)
Visit: http://localhost:8000/docs for interactive API documentation.

### Option B: Using curl

**Health check (no auth):**
```bash
curl http://localhost:8000/health
```

**Upload Contacts (Admin Only):**
```bash
curl -X POST http://localhost:8000/upload-contacts \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "Owners": {
      "it_team": {
        "admin1": {"email": "admin1@example.com", "phone_number": "0501111111"}
      }
    }
  }'
```

**Send Email (Direct to address):**
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

**Send SMS (To owner group):**
```bash
curl -X POST http://localhost:8000/send-sms \
  -H "Content-Type: application/json" \
  -u "admin:changeme" \
  -d '{
    "owner": "it_team",
    "text": "System Alert via SMS!",
    "recipient_type": 0
  }'
```

**Send Email (Bearer Token Auth):**
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

## Troubleshooting

### SSL/TLS Certificate Verification Errors
- If connecting to an internal/organization SMTP server or SMS gateway with a custom or self-signed certificate, you may get `[SSL: CERTIFICATE_VERIFY_FAILED]`.
- **Fix 1 (Preferred):** Provide the path to your organization's CA certificate using `SMTP_CA_CERT_PATH=/path/to/cert.pem` or `SMS_CA_CERT_PATH=/path/to/cert.pem`.
- **Fix 2 (Testing):** Set `SMTP_SSL_VERIFY=False` or `SMS_SSL_VERIFY=False` in `.env` to ignore certificate errors.

### "SMTP Authentication failed"
- Verify credentials in `.env`
- For Gmail: Use app password, not regular password. Ensure 2FA is enabled.

### "SMTP connect error" or Timeout
- Check that the server supports the port (25, 465, 587)
- Try explicitly setting `SMTP_TLS_MODE` to `starttls`, `implicit`, or `none`.

### Mutual Exclusion Error (422 Unprocessable Entity)
- "You must provide exactly one of 'to' or 'owner'"
- You cannot send an email/SMS using BOTH a direct list and an owner group in the same request. Pick one.

### SMS sending fails
- Verify `SMS_API_URL` is reachable
- Check gateway credentials (`SMS_CLIENT_ID`, `SMS_CLIENT_SECRET`, `SMS_SCOPE`)
- Inspect `logs/service.log` for HTTP/SSL error details.

## Support
For detailed architecture and API definitions, see `instractions/ARCHITECTURE.md` and `README.md`.
For code examples in Python, see `Tests_and_examples/examples.py`.
