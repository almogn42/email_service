# Changelog

## [1.0.5] — 2026-06-25

### Uvicorn Web Server Logs Captured to App Log File

**Problem:**
Uvicorn (the ASGI web server) has its own internal loggers (`uvicorn`, `uvicorn.error`, `uvicorn.access`) that do not propagate to the root Python logger by default. This meant HTTP access logs (incoming request lines, response status codes) were only printed to the console and were never written to `logs/app.log`.

**Fix — `main.py`:**
After setting up the `RotatingFileHandler`, all three Uvicorn loggers are explicitly given the same handler:
```python
for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    uvicorn_logger = logging.getLogger(uvicorn_logger_name)
    uvicorn_logger.addHandler(file_handler)
```
Console output and the `logs/app.log` file now contain identical log lines.

### Swagger UI Examples
Added rich `openapi_examples` for all POST endpoints (`/send-email`, `/send-email/token`, `/send-sms`, `/send-sms/token`) so the Swagger UI at `/docs` shows three pre-filled example payloads: *Direct Recipients*, *Single Owner Group*, and *Multiple Owner Groups*.

---

## [1.0.3] — 2026-05-15

### Multi-Owner Support + SMS SSL + Owner Bug Fix

#### Multi-Owner Support
The `owner` field on both `SendEmailRequest` and `SendSmsRequest` now accepts either a **single group name** (string) or a **list of group names**:

```json
{ "owner": "it_team", ... }          // single group — unchanged
{ "owner": ["it_team", "dev_team"], ... }  // multiple groups — new
```

Recipients from all specified groups are merged and **deduplicated** before sending. Implemented in `models.py` (`Union[str, List[str]]`), `owner_contacts.py` (`resolve_emails()`, `resolve_phones()`), and `main.py` handlers.

#### Bug Fix — `/send-sms/token` ignored `owner`
The `/send-sms/token` (Bearer token) endpoint was sending to `request.recipient` unconditionally, ignoring any `owner` value. Fixed by adding the same `resolve_phones(request.owner) if request.owner` logic that the Basic Auth endpoint already had.

#### SSL / CA Certificate Support for SMS Gateway
Two new settings control TLS behaviour when calling the external SMS gateway:

| Setting | Default | Description |
|---|---|---|
| `SMS_SSL_VERIFY` | `True` | Set `False` to disable SSL certificate verification for the SMS gateway |
| `SMS_CA_CERT_PATH` | `""` | Path to a custom CA certificate file (`.pem` / `.crt`) for the SMS gateway |

`httpx` is configured at call time based on these values:
- `SMS_SSL_VERIFY=True` + empty `SMS_CA_CERT_PATH` → system CA bundle (default)
- `SMS_CA_CERT_PATH` set → uses the specified CA file
- `SMS_SSL_VERIFY=False` → disables all certificate validation (development/testing only)

---

## [1.0.4] — 2026-04-26

### 🐛 Bug Fix — Logs were not written to file

**Problem:**  
All log messages (`logger.info`, `logger.error`, `logger.warning`) across every module were only printed to the console (stderr).  
The `docker-compose.yml` already mounted a volume `./logs:/app/logs`, but nothing in the application actually wrote log files there.  
This meant **all logs were lost on container restart**.

---

### Changes Made

#### 1. `config.py` — Added logging configuration settings

Three new fields were added to the `Settings` class so operators can control log file behavior via `.env` or environment variables without changing code:

| Setting | Default | Description |
|---|---|---|
| `LOG_DIR` | `"logs"` | Directory for log files (relative to app root, or absolute path) |
| `LOG_MAX_BYTES` | `5242880` (5 MB) | Maximum size of a single log file before rotation |
| `LOG_BACKUP_COUNT` | `5` | Number of old rotated log files to keep |

```python
# ── Logging Settings ───────────────────────────────────────────
LOG_DIR: str = "logs"
LOG_MAX_BYTES: int = 5242880
LOG_BACKUP_COUNT: int = 5
```

#### 2. `main.py` — Added `RotatingFileHandler` alongside console output

The `logging.basicConfig()` call was updated from a single console handler to **two handlers**:

| Handler | Destination | Purpose |
|---|---|---|
| `StreamHandler()` | stderr (console) | Visible via `docker logs` and terminal |
| `RotatingFileHandler()` | `logs/service.log` | Persisted to disk; survives restarts |

The `logs/` directory is created automatically on startup if it doesn't exist.

**Before:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**After:**
```python
import os
from logging.handlers import RotatingFileHandler

_settings = get_settings()

LOG_DIR = (
    _settings.LOG_DIR
    if os.path.isabs(_settings.LOG_DIR)
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), _settings.LOG_DIR)
)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(LOG_DIR, "service.log")

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=_settings.LOG_MAX_BYTES,
            backupCount=_settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {LOG_FILE}")
```

---

### No changes required in other modules

`email_sender.py`, `sms_sender.py`, `owner_contacts.py`, and `auth.py` all use `logging.getLogger(__name__)`, which automatically inherits the root logger's handlers.  
Their log messages now go to both console **and** the log file with zero code changes.

---

### Docker behavior

| What | How |
|---|---|
| `docker logs <container>` | Shows console output from `StreamHandler` (unchanged) |
| `./logs/service.log` on host | Created by `RotatingFileHandler`, persisted via the existing `./logs:/app/logs` volume mount |
| Log rotation | Automatically rotates at 5 MB; keeps 5 backups (~30 MB max) |

### Optional `.env` overrides

```env
LOG_DIR=/var/log/email-service
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=10
```
