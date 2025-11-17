# Vessel Documents Alert System

A modular, scalable alert system for monitoring database events and sending automated email notifications. Built with a plugin-based architecture that makes it easy to create new alert types by copying and customizing the project.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Creating New Alert Projects](#creating-new-alert-projects)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## 🎯 Overview

This system monitors a PostgreSQL database for vessel document updates and sends automated email notifications to vessel-specific recipients with company-specific CC lists. The modular architecture allows you to easily create new alert types (hot works, certifications, surveys, etc.) by copying this project and customizing the alert logic.

**Current Alert Type**: Vessel Document Updates
- Monitors `vessel_documents` table for records updated in the last 24 hours
- Sends individual emails to each vessel
- Automatically determines CC recipients based on vessel email domain
- Tracks sent notifications to prevent duplicates

---

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (Entry Point)                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
    ┌─────▼──────┐           ┌─────▼──────┐
    │ AlertConfig│           │  Scheduler  │
    │            │           │             │
    └─────┬──────┘           └─────┬───────┘
          │                        │
          │              ┌─────────┴──────────┐
          │              │                     │
    ┌─────▼──────┐  ┌───▼────────┐    ┌─────▼────────┐
    │  Tracker   │  │ BaseAlert  │    │    Alert     │
    │            │  │ (Abstract) │    │  Subclass    │
    └────────────┘  └─────┬──────┘    └──────┬───────┘
                          │                   │
                    ┌─────┴────────┬─────────┴────────┐
                    │              │                   │
            ┌───────▼────┐  ┌──────▼──────┐   ┌──────▼──────┐
            │EmailSender │  │ Formatters  │   │  db_utils   │
            └────────────┘  └─────────────┘   └─────────────┘
```

### Module Breakdown

| Module | Purpose | Reusable? |
|--------|---------|-----------|
| **src/core/** | Core infrastructure (config, tracking, scheduling, base alert class) | ✅ Yes - shared across all alerts |
| **src/notifications/** | Email and Teams notification handlers | ✅ Yes - shared across all alerts |
| **src/formatters/** | HTML and plain text email templates | ✅ Yes - shared across all alerts |
| **src/utils/** | Validation, image loading utilities | ✅ Yes - shared across all alerts |
| **src/alerts/** | Alert-specific implementations | ❌ No - customized per alert type |
| **queries/** | SQL query files | ❌ No - customized per alert type |

---

## ✨ Features

### Current Features
- ✅ **Modular Architecture**: Plugin-based design for easy extensibility
- ✅ **Email Notifications**: Rich HTML emails with company logos and responsive design
- ✅ **Smart Routing**: Automatic CC list selection based on email domain
- ✅ **Duplicate Prevention**: Tracks sent events to avoid re-sending notifications
- ✅ **Timezone Aware**: All datetime operations respect configured timezone
- ✅ **Dry-Run Mode**: Test without sending emails (triple-layer safety checks)
- ✅ **Graceful Shutdown**: SIGTERM/SIGINT handlers for clean termination
- ✅ **Error Recovery**: Continues running after transient failures
- ✅ **Docker Support**: Fully containerized with docker-compose
- ✅ **Atomic File Operations**: Prevents data corruption on interruption
- ✅ **Configurable Scheduling**: Run on any frequency (hourly, daily, etc.)
- ✅ **Comprehensive Logging**: Rotating logs with detailed execution traces

### Future Features (Stubs Ready)
- 🔜 **Microsoft Teams Integration**: Send notifications to Teams channels
- 🔜 **Slack Integration**: Send notifications to Slack channels
- 🔜 **Multiple Alert Types**: Hot works, certifications, surveys, etc.

---

## Prerequisites

### Required Software
- **Python 3.13+**
- **Docker & Docker Compose** (for containerized deployment)
- **PostgreSQL** database (remote or local)
- **SSH key** (if using SSH tunnel to database)

### Required Python Packages

See `requirements.txt` for exact versions. Key dependencies:

**Core Dependencies**:
- `python-decouple==3.8` - Environment variable management
- `pandas==2.3.3` - Data manipulation and analysis
- `sqlalchemy==2.0.44` - Database ORM and connection pooling
- `psycopg2-binary==2.9.11` - PostgreSQL adapter
- `sshtunnel>=0.4.0,<1.0.0` - SSH tunnel for remote database access
- `paramiko>=2.12.0,<4.0.0` - SSH protocol implementation (required by sshtunnel)
- `pymsteams==0.2.5` - Microsoft Teams webhook integration

**Testing Dependencies** (optional, for development):
- `pytest==7.4.3` - Testing framework
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-mock==3.12.0` - Mocking utilities
- `freezegun==1.4.0` - Time mocking for tests

Install all dependencies:
```bash
pip install -r requirements.txt
```

Install only production dependencies (exclude testing):
```bash
grep -v "^#\|pytest\|freezegun" requirements.txt | pip install -r /dev/stdin
```

### Required Accounts/Access
- SMTP server credentials
- PostgreSQL database credentials
- SSH access to database server (if using SSH tunnel)

---

## Installation

### Local Development Setup

1. **Clone or copy the project**:
   ```bash
   cd ~/Dev
   cp -r vessel-documents-alerts my-new-alerts
   cd my-new-alerts
   ```

2. **Create virtual environment**:
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**:
   ```bash
   cp .env.example .env
   vim .env  # Edit with your settings
   ```

5. **Test the configuration**:
   ```bash
   python -m src.main --dry-run --run-once
   ```

---

## Configuration

### Environment Variables (`.env`)

Create a `.env` file in the project root with the following variables:

```bash
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASS=your_password

# SSH Tunnel (optional - set USE_SSH_TUNNEL=True if needed)
USE_SSH_TUNNEL=False
SSH_HOST=your.server.com
SSH_PORT=22
SSH_USER=your_ssh_user
SSH_KEY_PATH=~/.ssh/your_key

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
SMTP_HOST=smtp.email.com
SMTP_PORT=465
SMTP_USER=sys@company.com
SMTP_PASS=your_app_password

# Internal recipients (always get notifications)
INTERNAL_RECIPIENTS=admin@company.com,manager@company.com

# Company-specific CC recipients (applied based on vessel email domain)
PROMINENCE_EMAIL_CC_RECIPIENTS=user1@prominencemaritime.com,user2@prominencemaritime.com
SEATRADERS_EMAIL_CC_RECIPIENTS=user1@seatraders.com,user2@seatraders.com

# ============================================================================
# FEATURE FLAGS
# ============================================================================
ENABLE_EMAIL_ALERTS=True
ENABLE_TEAMS_ALERTS=False
ENABLE_SPECIAL_TEAMS_EMAIL_ALERT=False
SPECIAL_TEAMS_EMAIL=False

# ============================================================================
# COMPANY BRANDING
# ============================================================================
PROMINENCE_LOGO=trans_logo_prominence_procreate_small.png
SEATRADERS_LOGO=trans_logo_seatraders_procreate_small.png

# ============================================================================
# SCHEDULING & TRACKING
# ============================================================================
BASE_URL=https://prominence.orca.tools
SCHEDULE_FREQUENCY_HOURS=24
TIMEZONE=Europe/Athens
REMINDER_FREQUENCY_DAYS=30
SENT_EVENTS_FILE=sent_alerts.json

# ============================================================================
# LOGGING
# ============================================================================
LOG_FILE=alerts.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

---

## Usage

### Command Line Options

```bash
# Dry-run mode (no emails sent - for testing)
python -m src.main --dry-run --run-once

# Run once and exit (sends real emails)
python -m src.main --run-once

# Run continuously with scheduling (sends real emails)
python -m src.main
```

### Expected Output (Dry-Run)

```
======================================================================
▶ ALERT SYSTEM STARTING
======================================================================
[OK] Configuration validation passed
======================================================================
🔒 DRY RUN MODE ACTIVATED - NO NOTIFICATIONS WILL BE SENT
======================================================================
[OK] Event tracker initialized
[OK] Email sender initialized (DRY-RUN MODE - will not send emails)
[OK] Formatters initialized
[OK] Registered VesselDocumentsAlert
============================================================
▶ RUN-ONCE MODE: Executing alerts once without scheduling
============================================================
Running 1 alert(s)...
Executing alert 1/1...
============================================================
▶ VesselDocumentsAlert RUN STARTED
============================================================
--> Fetching data from database...
[OK] Fetched 7781 record(s)
--> Applying filtering logic...
[OK] Filtered to 29 document(s) updated in last 1 day(s)
--> Checking for previously sent notifications...
[OK] 29 new record(s) to notify
--> Routing notifications to recipients...
[OK] Created notification job for vessel 'KNOSSOS' (3 document(s))
[OK] Created notification job for vessel 'MINI' (25 document(s))
[OK] Created notification job for vessel 'NONDAS' (1 document(s))
[OK] Created 3 notification job(s)
--> Sending notification 1/3...
[DRY-RUN] Notification 1 prepared but NOT sent (emails disabled)
[DRY-RUN] Would send to: knossos@vsl.prominencemaritime.com
[DRY-RUN] Would CC: user1@prominencemaritime.com
[DRY-RUN] Subject: 3 Vessel Document Updates - KNOSSOS
[DRY-RUN] Records: 3
...
[DRY-RUN] Would mark 29 event(s) as sent (tracking disabled in dry-run)
◼ VesselDocumentsAlert RUN COMPLETE
```

---

## 🔄 Creating New Alert Projects

The modular design makes it easy to create new alert types by copying this project. Here's how:

### Option 1: Manual Copy (Simple)

1. **Copy the entire project**:
   ```bash
   cd ~/Dev
   cp -r vessel-documents-alerts hot-works-alerts
   cd hot-works-alerts
   ```

2. **Clean up old data**:
   ```bash
   rm -rf data/*.json logs/*.log
   git init  # Start fresh git history if desired
   ```

3. **Update `.env` configuration**:
   ```bash
   vim .env
   ```
   Change:
   - `SCHEDULE_FREQUENCY_HOURS` (e.g., `0.5` for hot works)
   - `REMINDER_FREQUENCY_DAYS` (e.g., `7` for hot works)
   - `INTERNAL_RECIPIENTS` (alert-specific recipients)
   - Any other alert-specific settings

4. **Update `docker-compose.yml`**:
   ```yaml
   services:
     alerts:
       container_name: hot-works-alerts-app  # CHANGE THIS
       # ... rest stays the same
   ```

5. **Create new SQL query**:
   ```bash
   rm queries/NewVesselCertificates.sql
   vim queries/EventHotWork.sql
   ```
   
   Write your SQL query that returns the columns you need.

6. **Create new alert implementation**:
   ```bash
   rm src/alerts/vessel_documents_alert.py
   vim src/alerts/hot_works_alert.py
   ```

   ```python
   """Hot Works Alert Implementation."""
   from typing import Dict, List
   import pandas as pd
   from datetime import datetime, timedelta
   from zoneinfo import ZoneInfo
   from sqlalchemy import text
   
   from src.core.base_alert import BaseAlert
   from src.core.config import AlertConfig
   from src.db_utils import get_db_connection, validate_query_file
   
   
   class HotWorksAlert(BaseAlert):
       """Alert for hot work permit reviews."""
       
       def __init__(self, config: AlertConfig):
           super().__init__(config)
           self.sql_query_file = 'EventHotWork.sql'
           self.lookback_days = 17
       
       def fetch_data(self) -> pd.DataFrame:
           """Fetch hot work permits from database."""
           query_path = self.config.queries_dir / self.sql_query_file
           query_sql = validate_query_file(query_path)
           query = text(query_sql)
           
           with get_db_connection() as conn:
               df = pd.read_sql_query(query, conn)
           
           self.logger.info(f"Fetched {len(df)} hot work permit(s)")
           return df
       
       def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
           """Filter for permits in review status within lookback period."""
           if df.empty:
               return df
           
           # Your filtering logic here
           # ...
           
           return df_filtered
       
       def route_notifications(self, df: pd.DataFrame) -> List[Dict]:
           """Route permits to appropriate recipients."""
           # Your routing logic here
           # ...
           
           return jobs
       
       def get_tracking_key(self, row: pd.Series) -> str:
           """Generate tracking key from permit ID."""
           return f"hotwork_{row['permit_id']}"
       
       def get_subject_line(self, data: pd.DataFrame, metadata: Dict) -> str:
           """Generate email subject line."""
           count = len(data)
           if count == 1:
               return "Hot Work Permit Requires Review"
           return f"{count} Hot Work Permits Require Review"
       
       def get_required_columns(self) -> List[str]:
           """Return required columns for this alert."""
           return ['permit_id', 'permit_name', 'created_at', 'vessel_email']
   ```

7. **Update `src/alerts/__init__.py`**:
   ```python
   """Alert implementations."""
   from .hot_works_alert import HotWorksAlert  # CHANGE THIS
   
   __all__ = ['HotWorksAlert']  # CHANGE THIS
   ```

8. **Update `src/main.py`** registration:
   ```python
   def register_alerts(scheduler: AlertScheduler, config: AlertConfig) -> None:
       """Register all alert implementations with the scheduler."""
       logger = logging.getLogger(__name__)
       
       # Register Hot Works Alert (CHANGE THIS)
       from src.alerts.hot_works_alert import HotWorksAlert
       hot_works_alert = HotWorksAlert(config)
       scheduler.register_alert(hot_works_alert.run)
       logger.info("[OK] Registered HotWorksAlert")
   ```

9. **Test the new alert**:
   ```bash
   python -m src.main --dry-run --run-once
   ```

10. **Deploy**:
    ```bash
    export UID=$(id -u) GID=$(id -g)
    docker-compose build
    docker-compose up -d
    ```

### Option 2: Automated Script (Advanced)

Create a script to automate the copy process:

**`scripts/create_new_alert_project.sh`**:
```bash
#!/bin/bash
# Usage: ./scripts/create_new_alert_project.sh hot-works-alerts HotWorksAlert

PROJECT_NAME=$1
ALERT_CLASS_NAME=$2

if [ -z "$PROJECT_NAME" ] || [ -z "$ALERT_CLASS_NAME" ]; then
    echo "Usage: $0 <project-name> <AlertClassName>"
    echo "Example: $0 hot-works-alerts HotWorksAlert"
    exit 1
fi

# Copy template
echo "📦 Copying project template..."
cp -r ../vessel-documents-alerts "../$PROJECT_NAME"
cd "../$PROJECT_NAME"

# Clean up old data
echo "🧹 Cleaning up old data..."
rm -rf data/*.json logs/*.log
rm -rf .git

# Update alert class name in files
echo "✏️  Updating alert class references..."
sed -i '' "s/VesselDocumentsAlert/$ALERT_CLASS_NAME/g" src/alerts/__init__.py
sed -i '' "s/VesselDocumentsAlert/$ALERT_CLASS_NAME/g" src/main.py

# Rename alert file
echo "📝 Renaming alert file..."
ALERT_FILE=$(echo $ALERT_CLASS_NAME | sed 's/\([A-Z]\)/_\L\1/g' | sed 's/^_//')".py"
mv src/alerts/vessel_documents_alert.py "src/alerts/$ALERT_FILE"

# Update container name in docker-compose.yml
echo "🐳 Updating Docker configuration..."
sed -i '' "s/new-vessel-certificates-app/$PROJECT_NAME-app/g" docker-compose.yml

# Initialize new git repo
git init

echo ""
echo "✅ New project created: $PROJECT_NAME"
echo ""
echo "📝 Next steps:"
echo "   1. cd ../$PROJECT_NAME"
echo "   2. Update .env with new configuration"
echo "   3. Add your SQL query to queries/"
echo "   4. Implement the alert logic in src/alerts/$ALERT_FILE"
echo "   5. Test: python -m src.main --dry-run --run-once"
echo "   6. Deploy: docker-compose up -d"
echo ""
```

Make it executable and use it:
```bash
chmod +x scripts/create_new_alert_project.sh
./scripts/create_new_alert_project.sh hot-works-alerts HotWorksAlert
```

---

## 🐳 Docker Deployment

### Building the Container

```bash
# Set user/group IDs for proper file permissions
export UID=$(id -u) GID=$(id -g)

# Build the image
docker-compose build
```

### Running in Production

```bash
# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f alerts

# Stop the container
docker-compose down

# Restart after config changes
docker-compose restart alerts

# View container status
docker-compose ps
```

### Docker Configuration

**`docker-compose.yml`**:
```yaml
services:
  alerts:
    build:
      context: .
      args:
        UID: ${UID}
        GID: ${GID}
    container_name: new-vessel-certificates-app
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs          # Logs persist on host
      - ./data:/app/data          # Tracking data persists on host
      - ./queries:/app/queries    # Mount queries for easy updates
      - /path/to/ssh_key:/app/ssh_key:ro  # SSH key (read-only)
    restart: unless-stopped        # Auto-restart on failure
```

### Health Monitoring

The Docker container includes a healthcheck that verifies:
- Log file exists
- Log file was updated recently (within schedule frequency + 10 minutes)

View healthcheck status:
```bash
docker inspect --format='{{.State.Health.Status}}' new-vessel-certificates-app
```

---

## 🛠️ Development

### Project Structure

```
vessel-documents-alerts/
├── .env                          # Configuration (not in git)
├── .env.example                  # Configuration template
├── .gitignore                    # Git ignore rules
├── docker-compose.yml            # Docker configuration
├── Dockerfile                    # Container definition
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── db_utils.py               # Database utilities
│   │
│   ├── core/                     # Core infrastructure (reusable)
│   │   ├── __init__.py
│   │   ├── base_alert.py         # Abstract base class for alerts
│   │   ├── config.py             # Configuration management
│   │   ├── tracking.py           # Event tracking system
│   │   └── scheduler.py          # Scheduling logic
│   │
│   ├── notifications/            # Notification handlers (reusable)
│   │   ├── __init__.py
│   │   ├── email_sender.py       # Email sending with SMTP
│   │   └── teams_sender.py       # Teams integration (stub)
│   │
│   ├── formatters/               # Email formatters (reusable)
│   │   ├── __init__.py
│   │   ├── html_formatter.py     # Rich HTML emails
│   │   └── text_formatter.py     # Plain text emails
│   │
│   ├── utils/                    # Utilities (reusable)
│   │   ├── __init__.py
│   │   ├── validation.py         # DataFrame validation
│   │   └── image_utils.py        # Logo loading
│   │
│   └── alerts/                   # Alert implementations (customized)
│       ├── __init__.py
│       └── vessel_documents_alert.py  # This project's alert
│
├── queries/                      # SQL queries (customized)
│   └── NewVesselCertificates.sql
│
├── media/                        # Company logos
│   ├── logo_prominence_maritime_teliko_new_1.png
│   └── trans_logo_seatraders_procreate_small.png
│
├── data/                         # Runtime data (not in git)
│   └── sent_alerts.json          # Tracking file
│
├── logs/                         # Log files (not in git)
│   └── alerts.log
│
└── tests/                        # Unit tests
    ├── conftest.py
    ├── test_notifications.py
    ├── test_tracking.py
    └── ...
```

### Adding a New Alert to Same Project

If you want **multiple alerts in one container** (not recommended, but possible):

1. **Create new alert class**:
   ```bash
   vim src/alerts/hot_works_alert.py
   ```

2. **Update `src/alerts/__init__.py`**:
   ```python
   from .vessel_documents_alert import VesselDocumentsAlert
   from .hot_works_alert import HotWorksAlert  # Add this
   
   __all__ = ['VesselDocumentsAlert', 'HotWorksAlert']
   ```

3. **Register both alerts in `src/main.py`**:
   ```python
   def register_alerts(scheduler: AlertScheduler, config: AlertConfig) -> None:
       # Vessel Documents
       vessel_docs = VesselDocumentsAlert(config)
       scheduler.register_alert(vessel_docs.run)
       
       # Hot Works
       hot_works = HotWorksAlert(config)
       scheduler.register_alert(hot_works.run)
   ```

**Note**: Both alerts will run on the **same schedule** (SCHEDULE_FREQUENCY_HOURS).

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_notifications.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "No module named 'src'"
**Cause**: Running from wrong directory or PYTHONPATH not set

**Solution**:
```bash
# Run from project root
cd /path/to/vessel-documents-alerts
python -m src.main --dry-run --run-once
```

#### 2. Emails not sending (even without --dry-run)
**Causes**:
- SMTP credentials incorrect
- Gmail blocking "less secure apps"
- Firewall blocking SMTP port

**Solution**:
```bash
# Check SMTP settings
echo $SMTP_HOST $SMTP_PORT $SMTP_USER

# For Gmail, use App Password, not regular password
# Enable 2FA, then generate app password at:
# https://myaccount.google.com/apppasswords

# Test SMTP connection
telnet smtp.gmail.com 465
```

#### 3. "Logo not found" warnings
**Cause**: Logo file doesn't exist at specified path

**Solution**:
```bash
# Check logo exists
ls -la media/logo_prominence_maritime_teliko_new_1.png

# Update .env if filename is different
PROMINENCE_LOGO=correct_filename.png
```

#### 4. Database connection fails
**Causes**:
- SSH tunnel not working
- Database credentials incorrect
- Database not accessible from this host

**Solution**:
```bash
# Test SSH connection
ssh -i /path/to/key user@host

# Test database connection
psql -h localhost -p 5432 -U username -d database_name

# Check .env settings
DB_HOST=...
DB_PORT=...
USE_SSH_TUNNEL=True/False
SSH_KEY_PATH=...
```

#### 5. "TypeError: Can't instantiate abstract class"
**Cause**: Alert class missing required methods

**Solution**: Implement all 6 required methods:
- `fetch_data()`
- `filter_data()`
- `route_notifications()`
- `get_tracking_key()`
- `get_subject_line()`
- `get_required_columns()`

#### 6. Timezone comparison errors
**Cause**: Mixing timezone-aware and timezone-naive datetimes

**Solution**: Ensure all datetime operations use timezone:
```python
from zoneinfo import ZoneInfo

# Always use timezone
cutoff = datetime.now(tz=ZoneInfo(self.config.timezone))

# Localize database datetimes
df['updated_at'] = df['updated_at'].dt.tz_localize('UTC').dt.tz_convert(self.config.timezone)
```

### Logging & Debugging

```bash
# View live logs (local)
tail -f logs/alerts.log

# View live logs (Docker)
docker-compose logs -f alerts

# Check last 100 lines
tail -n 100 logs/alerts.log

# Search logs for errors
grep ERROR logs/alerts.log

# Check tracking file
cat data/sent_alerts.json | jq '.'
```

### Testing Checklist

Before production:
- [ ] Dry-run completes without errors
- [ ] SQL query returns expected columns
- [ ] Email recipients configured correctly
- [ ] CC recipients configured correctly
- [ ] Logos display in emails
- [ ] Tracking file updates after send
- [ ] No duplicates on second run
- [ ] Docker build succeeds
- [ ] Docker container stays running
- [ ] Logs rotate properly

---

## 📚 Key Concepts

### Abstract Base Class Pattern

The `BaseAlert` class defines a **contract** that all alerts must follow:

```python
class BaseAlert(ABC):
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """Fetch data from database."""
        pass
    
    # ... 5 more abstract methods ...
    
    def run(self) -> bool:
        """Complete workflow - already implemented!"""
        df = self.fetch_data()
        df_filtered = self.filter_data(df)
        jobs = self.route_notifications(df_filtered)
        self._send_notifications(jobs)
```

**Benefits**:
- You write ~80 lines (alert-specific logic)
- You get ~300 lines free (infrastructure, error handling, logging)
- Python enforces you implement all required methods
- All alerts work consistently

### Configuration Flow

```
.env file
  ↓
python-decouple reads file
  ↓
AlertConfig.from_env() parses values
  ↓
AlertConfig instance created
  ↓
Passed to all components
  ↓
Accessed via self.config
```

### Tracking System

```
Event happens in database
  ↓
Alert detects it
  ↓
Check if already sent (tracking_key in sent_alerts.json)
  ↓
If new: send notification + save tracking_key with timestamp
  ↓
If old: skip (already sent within REMINDER_FREQUENCY_DAYS)
```

---

## 📞 Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `tail -f logs/alerts.log`
3. Test in dry-run mode: `python -m src.main --dry-run --run-once`
4. Contact: data@prominencemaritime.com

---

## 📄 License

Proprietary - Prominence Maritime / Seatraders

---

## 🎉 Quick Start Summary

```bash
# 1. Copy project
cp -r vessel-documents-alerts my-new-alert
cd my-new-alert

# 2. Configure
vim .env

# 3. Test
python -m src.main --dry-run --run-once

# 4. Deploy
export UID=$(id -u) GID=$(id -g)
docker-compose up -d

# 5. Monitor
docker-compose logs -f alerts
```

**That's it!**
