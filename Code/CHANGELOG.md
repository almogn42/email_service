# Changelog

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
