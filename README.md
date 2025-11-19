# Vessel Documents Alert System

A modular, production-ready alert system for monitoring database events and sending automated email notifications. Built with a plugin-based architecture that makes it easy to create new alert types by copying and customizing the project.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
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
- Optional reminder system after configurable days

---

## 🏗️ Architecture

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                      (Entry Point)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
    ┌─────▼──────┐           ┌──────▼──────┐
    │ AlertConfig│           │  Scheduler  │
    │            │           │             │
    └─────┬──────┘           └─────┬───────┘
          │                        │
          │               ┌────────┴──────────┐
          │               │                   │
    ┌─────▼──────┐  ┌─────▼──────┐    ┌───────▼──────┐
    │  Tracker   │  │ BaseAlert  │    │    Alert     │
    │            │  │ (Abstract) │    │  Subclass    │
    └────────────┘  └─────┬──────┘    └──────┬───────┘
                          │                  │
                    ┌─────┴────────┬─────────┴───────┐
                    │              │                 │
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
- ✅ **Optional Reminders**: Re-send alerts after configurable days (or never)
- ✅ **Timezone Aware**: All datetime operations respect configured timezone
- ✅ **Dry-Run Mode**: Test without sending emails (redirects to test addresses)
- ✅ **Command-Line Overrides**: `--dry-run` flag overrides `.env` settings
- ✅ **Graceful Shutdown**: SIGTERM/SIGINT handlers for clean termination
- ✅ **Error Recovery**: Continues running after transient failures
- ✅ **Docker Support**: Fully containerized with docker-compose
- ✅ **SSH Tunnel Support**: Secure remote database access
- ✅ **Atomic File Operations**: Prevents data corruption on interruption
- ✅ **Configurable Scheduling**: Run on any frequency (hourly, daily, etc.)
- ✅ **Comprehensive Logging**: Rotating logs with detailed execution traces
- ✅ **Comprehensive Tests**: 59% code coverage with unit and integration tests

### Future Features (Planned)
- 🔜 **Document Links**: Clickable links to documents in emails *(not yet implemented)*
- 🔜 **Microsoft Teams Integration**: Send notifications to Teams channels
- 🔜 **Slack Integration**: Send notifications to Slack channels
- 🔜 **Multiple Alert Types**: Hot works, certifications, surveys, etc.

---

## 📋 Prerequisites

### Required Software
- **Python 3.13+**
- **Docker & Docker Compose** (recommended for deployment)
- **PostgreSQL** database (remote or local)
- **SSH key** (if using SSH tunnel to database)

### Required Python Packages

See `requirements.txt` for exact versions. Key dependencies:

**Core Dependencies**:
- `python-decouple==3.8` - Environment variable management
- `pandas==2.2.3` - Data manipulation and analysis
- `sqlalchemy==2.0.44` - Database ORM and connection pooling
- `psycopg2-binary==2.9.11` - PostgreSQL adapter
- `sshtunnel>=0.4.0,<1.0.0` - SSH tunnel for remote database access
- `paramiko>=2.12.0,<4.0.0` - SSH protocol implementation (required by sshtunnel)
- `pymsteams==0.2.5` - Microsoft Teams webhook integration *(planned)*

**Testing Dependencies**:
- `pytest==7.4.3` - Testing framework
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-mock==3.12.0` - Mocking utilities

**Install all dependencies**:
```bash
pip install -r requirements.txt
```

**Install only production dependencies** (exclude testing):
```bash
grep -v "^#\|pytest" requirements.txt | pip install -r /dev/stdin
```

### Required Accounts/Access
- SMTP server credentials (e.g., Gmail, Office365)
- PostgreSQL database credentials
- SSH access to database server (if using SSH tunnel)

---

## 🚀 Installation

### Docker Deployment (Recommended)

1. **Clone or copy the project**:
```bash
   cd ~/Dev
   git clone <repository> vessel-documents-alerts
   cd vessel-documents-alerts
```

2. **Create `.env` file**:
```bash
   cp .env.example .env
   vim .env  # Edit with your settings
```

3. **Build and run**:
```bash
   export UID=$(id -u) GID=$(id -g)
   docker-compose build
   docker-compose up -d
```

4. **Verify it's running**:
```bash
   docker-compose logs -f alerts
```

### Local Development Setup

1. **Clone or copy the project**:
```bash
   cd ~/Dev
   git clone <repository> vessel-documents-alerts
   cd vessel-documents-alerts
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

## ⚙️ Configuration

### Environment Variables (`.env`)

Create a `.env` file in the project root with the following variables:
```bash
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_HOST=your.database.host.com
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASS=your_password

# SSH Tunnel (set USE_SSH_TUNNEL=True if database requires SSH tunnel)
USE_SSH_TUNNEL=True
SSH_HOST=your.ssh.host.com
SSH_PORT=22
SSH_USER=your_ssh_user
SSH_KEY_PATH=/app/ssh_ubuntu_key

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=alerts@yourcompany.com
SMTP_PASS=your_app_password

# Internal recipients (always receive all notifications)
INTERNAL_RECIPIENTS=admin@company.com,manager@company.com

# Company-specific CC recipients (applied based on vessel email domain)
PROMINENCE_EMAIL_CC_RECIPIENTS=user1@prominencemaritime.com,user2@prominencemaritime.com
SEATRADERS_EMAIL_CC_RECIPIENTS=user1@seatraders.com,user2@seatraders.com

# ============================================================================
# DRY-RUN / TESTING CONFIGURATION
# ============================================================================
# Set DRY_RUN=True to redirect ALL emails to test addresses (no real emails sent)
# Command-line flag --dry-run overrides this setting
DRY_RUN=False

# When DRY_RUN=True, all emails are redirected to these addresses (comma-separated)
DRY_RUN_EMAIL=test1@company.com,test2@company.com

# ============================================================================
# FEATURE FLAGS
# ============================================================================
ENABLE_EMAIL_ALERTS=True
ENABLE_TEAMS_ALERTS=False
ENABLE_SPECIAL_TEAMS_EMAIL_ALERT=False

# Document links (not yet implemented)
ENABLE_DOCUMENT_LINKS=False
BASE_URL=https://prominence.orca.tools

# ============================================================================
# COMPANY BRANDING
# ============================================================================
PROMINENCE_LOGO=trans_logo_prominence_procreate_small.png
SEATRADERS_LOGO=trans_logo_seatraders_procreate_small.png

# ============================================================================
# SCHEDULING & TRACKING
# ============================================================================
# How often to check for new alerts (in hours)
# Examples: 24 = daily, 0.5 = every 30 minutes, 168 = weekly
SCHEDULE_FREQUENCY_HOURS=24

# Timezone for all datetime operations
TIMEZONE=Europe/Athens

# Reminder frequency (in days)
# - Set to a number (e.g., 30) to re-send alerts after X days
# - Leave blank or empty to NEVER re-send (track forever, no reminders)
REMINDER_FREQUENCY_DAYS=

# File where sent events are tracked (relative to project root)
SENT_EVENTS_FILE=sent_alerts.json

# ============================================================================
# ALERT-SPECIFIC CONFIGURATION
# ============================================================================
# How many days back to look for vessel document updates
VESSEL_DOCUMENTS_LOOKBACK_DAYS=1

# ============================================================================
# LOGGING
# ============================================================================
LOG_FILE=alerts.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

### Configuration Notes

**SSH Tunnel**:
- Set `USE_SSH_TUNNEL=True` if your database is only accessible via SSH
- `SSH_KEY_PATH` should point to your private SSH key file
- In Docker, mount your SSH key as read-only: `~/.ssh/your_key:/app/ssh_ubuntu_key:ro`

**DRY_RUN Mode**:
- `DRY_RUN=True` in `.env` → All emails redirected to `DRY_RUN_EMAIL` addresses
- `--dry-run` command-line flag → Overrides `.env`, enables dry-run mode
- **Three-layer safety**: Even with `DRY_RUN=False`, code checks prevent accidental sends

**REMINDER_FREQUENCY_DAYS**:
- **Empty/blank** → Never re-send notifications (track events forever)
- **Number** (e.g., `30`) → Re-send notifications after X days
- Events older than X days are removed from tracking file

**Email Routing**:
- System extracts domain from vessel email (e.g., `vessel@vsl.prominencemaritime.com` → `prominencemaritime.com`)
- Matches domain to CC list (e.g., `PROMINENCE_EMAIL_CC_RECIPIENTS`)
- Falls back to `INTERNAL_RECIPIENTS` if no match found

---

## 🎮 Usage

### Command Line Options
```bash
# Dry-run mode (redirects emails to DRY_RUN_EMAIL addresses)
python -m src.main --dry-run --run-once

# Run once and exit (sends real emails based on .env DRY_RUN setting)
python -m src.main --run-once

# Run continuously with scheduling (production mode)
python -m src.main

# Docker equivalent commands
docker-compose run --rm alerts python -m src.main --dry-run --run-once
docker-compose run --rm alerts python -m src.main --run-once
docker-compose up -d  # Runs continuously
```

### Command-Line Flags

| Flag | Effect | Overrides .env? |
|------|--------|-----------------|
| `--dry-run` | Redirects all emails to `DRY_RUN_EMAIL` | Yes - forces dry-run ON |
| `--run-once` | Executes once and exits (no scheduling) | No |
| (none) | Runs continuously on schedule | No |

### Expected Output (Dry-Run)
```
======================================================================
▶ ALERT SYSTEM STARTING
======================================================================
[OK] Configuration validation passed
======================================================================
🔒 DRY RUN MODE ACTIVATED - EMAILS REDIRECTED TO: test@company.com
======================================================================
[OK] Event tracker initialized
[OK] Email sender initialized (DRY-RUN MODE - emails redirected)
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
[DRY-RUN] Email redirected to: test@company.com
[DRY-RUN] Original recipient: knossos@vsl.prominencemaritime.com
[DRY-RUN] Original CC: user1@prominencemaritime.com, user2@prominencemaritime.com
[DRY-RUN] Subject: AlertDev | KNOSSOS | 3 Vessel Document Updates
[OK] Sent notification 1/3
...
[OK] Marked 29 event(s) as sent
◼ VesselDocumentsAlert RUN COMPLETE
```

### Production Output
```
======================================================================
▶ ALERT SYSTEM STARTING
======================================================================
[OK] Configuration validation passed
[OK] Event tracker initialized
[OK] Email sender initialized
[OK] Formatters initialized
[OK] Registered VesselDocumentsAlert
============================================================
▶ PRODUCTION MODE: Running on schedule (every 24.0 hours)
============================================================
[OK] Next run at: 2025-11-20 14:30:00 EET
Running 1 alert(s)...
...
[OK] Sent notification to knossos@vsl.prominencemaritime.com
[OK] CC: user1@prominencemaritime.com, user2@prominencemaritime.com
[OK] Marked 29 event(s) as sent
◼ VesselDocumentsAlert RUN COMPLETE
[OK] Sleeping until next run...
```

---

## 🧪 Testing

### Running Tests

**Local (requires pytest installed)**:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term --cov-report=html

# Run specific test file
pytest tests/test_config.py -v

# Run specific test
pytest tests/test_tracking.py::test_tracker_marks_events_as_sent -v
```

**Docker (recommended)**:
```bash
# Run all tests
docker-compose run --rm alerts pytest tests/ -v

# Run with coverage
docker-compose run --rm alerts pytest tests/ --cov=src --cov-report=term

# Interactive shell (run multiple test commands)
docker-compose run --rm alerts bash
> pytest tests/ -v
> pytest tests/test_integration.py -v
> exit
```

### Test Coverage

Current coverage: **59%** overall

| Module | Coverage | Status |
|--------|----------|--------|
| `src/core/config.py` | 98% | ✅ Excellent |
| `src/formatters/text_formatter.py` | 95% | ✅ Excellent |
| `src/formatters/html_formatter.py` | 91% | ✅ Excellent |
| `src/alerts/vessel_documents_alert.py` | 88% | ✅ Good |
| `src/core/base_alert.py` | 74% | ✅ Good |
| `src/core/tracking.py` | 71% | ⚠️ Acceptable |
| `src/notifications/email_sender.py` | 57% | ⚠️ Acceptable |
| `src/core/scheduler.py` | 47% | ⚠️ Needs work |
| `src/db_utils.py` | 32% | ⚠️ Needs work |
| `src/main.py` | 0% | ❌ Not tested (entry point) |

**View detailed coverage report**:
```bash
# Generate HTML report
docker-compose run --rm alerts pytest tests/ --cov=src --cov-report=html

# Open in browser (local development)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Structure
```
tests/
├── conftest.py                    # Shared fixtures and test configuration
├── test_config.py                 # Configuration loading and validation
├── test_tracking.py               # Event tracking and duplicate prevention
├── test_vessel_documents_alert.py # Alert logic and routing
├── test_formatters.py             # Email HTML/text generation
├── test_email_sender.py           # Email sending functionality
├── test_scheduler.py              # Scheduling and execution
└── test_integration.py            # End-to-end workflow tests
```

### Writing New Tests

When adding a new alert type, create corresponding tests:
```python
# tests/test_my_new_alert.py
import pytest
from src.alerts.my_new_alert import MyNewAlert


def test_alert_initializes_correctly(mock_config):
    """Test that alert initializes with correct configuration."""
    alert = MyNewAlert(mock_config)
    assert alert.sql_query_file == 'MyQuery.sql'
    assert alert.lookback_days == 7


def test_alert_filters_data_correctly(mock_config, sample_dataframe):
    """Test filtering logic."""
    alert = MyNewAlert(mock_config)
    filtered = alert.filter_data(sample_dataframe)
    assert len(filtered) > 0
```

---

## 🔄 Creating New Alert Projects

The modular design makes it easy to create new alert types. **Recommended approach**: Copy entire project to new directory (one alert per container).

### Step-by-Step Guide

#### 1. Copy the Project
```bash
cd ~/Dev
cp -r vessel-documents-alerts hot-works-alerts
cd hot-works-alerts
```

#### 2. Clean Up Old Data
```bash
rm -rf data/*.json logs/*.log
rm -rf .git  # Optional: start fresh git history
git init
```

#### 3. Update Configuration

**Edit `.env`**:
```bash
vim .env
```

Key changes for new alert type:
```bash
# Change schedule (e.g., every 30 minutes for hot works)
SCHEDULE_FREQUENCY_HOURS=0.5

# Change reminder frequency (e.g., weekly reminders)
REMINDER_FREQUENCY_DAYS=7

# Update recipients for this alert type
INTERNAL_RECIPIENTS=hotworks-admin@company.com

# Update lookback period
HOT_WORKS_LOOKBACK_DAYS=17  # Add new variable
```

#### 4. Update Docker Configuration

**Edit `docker-compose.yml`**:
```yaml
services:
  alerts:
    build:
      context: .
      args:
        UID: ${UID}
        GID: ${GID}
    container_name: hot-works-alerts-app  # ← CHANGE THIS
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./queries:/app/queries
      - ~/.ssh/your_key:/app/ssh_key:ro
    restart: unless-stopped
```

#### 5. Create SQL Query
```bash
rm queries/NewVesselCertificates.sql
vim queries/EventHotWork.sql
```

**Example query**:
```sql
SELECT 
    event_id,
    event_name,
    vessel_id,
    vessel_name,
    vessel_email,
    created_at,
    status,
    reviewer_notes
FROM hot_work_permits
WHERE status = 'pending_review'
ORDER BY created_at DESC;
```

#### 6. Create Alert Implementation
```bash
rm src/alerts/vessel_documents_alert.py
vim src/alerts/hot_works_alert.py
```

**Template**:
```python
"""Hot Works Alert Implementation."""
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.core.base_alert import BaseAlert
from src.core.config import AlertConfig
from src.db_utils import get_db_connection, validate_query_file


class HotWorksAlert(BaseAlert):
    """Alert for hot work permit reviews."""
    
    def __init__(self, config: AlertConfig):
        """Initialize hot works alert."""
        super().__init__(config)
        self.sql_query_file = 'EventHotWork.sql'
        self.lookback_days = 17  # Look back 17 days
    
    def fetch_data(self) -> pd.DataFrame:
        """Fetch hot work permits from database."""
        query_path = self.config.queries_dir / self.sql_query_file
        query_sql = validate_query_file(query_path)
        
        with get_db_connection() as conn:
            df = pd.read_sql_query(query_sql, conn)
        
        self.logger.info(f"Fetched {len(df)} hot work permit(s)")
        return df
    
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter for permits in review status within lookback period."""
        if df.empty:
            return df
        
        # Ensure timezone awareness
        tz = ZoneInfo(self.config.timezone)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_localize('UTC').dt.tz_convert(tz)
        
        # Filter by lookback period
        cutoff = datetime.now(tz=tz) - timedelta(days=self.lookback_days)
        df_filtered = df[df['created_at'] >= cutoff].copy()
        
        self.logger.info(
            f"Filtered to {len(df_filtered)} permit(s) created in last {self.lookback_days} day(s)"
        )
        return df_filtered
    
    def route_notifications(self, df: pd.DataFrame) -> List[Dict]:
        """Route permits to appropriate recipients."""
        if df.empty:
            return []
        
        jobs = []
        
        # Group by vessel
        for vessel_id, group in df.groupby('vessel_id'):
            vessel_name = group.iloc[0]['vessel_name']
            vessel_email = group.iloc[0]['vessel_email']
            
            # Determine CC recipients based on email domain
            domain = vessel_email.split('@')[-1]
            cc_recipients = self._get_cc_recipients_for_domain(domain)
            
            job = {
                'recipients': [vessel_email],
                'cc_recipients': cc_recipients,
                'data': group,
                'metadata': {
                    'alert_title': 'Hot Work Permits Requiring Review',
                    'vessel_name': vessel_name,
                    'vessel_id': vessel_id,
                    'display_columns': ['event_name', 'created_at', 'status', 'reviewer_notes']
                }
            }
            
            jobs.append(job)
            self.logger.info(
                f"[OK] Created notification job for vessel '{vessel_name}' ({len(group)} permit(s))"
            )
        
        return jobs
    
    def get_tracking_key(self, row: pd.Series) -> str:
        """Generate unique tracking key from permit ID."""
        return f"hotwork_{row['event_id']}"
    
    def get_subject_line(self, data: pd.DataFrame, metadata: Dict) -> str:
        """Generate email subject line."""
        count = len(data)
        vessel_name = metadata.get('vessel_name', 'Unknown')
        
        if count == 1:
            return f"AlertDev | {vessel_name} | Hot Work Permit Requires Review"
        return f"AlertDev | {vessel_name} | {count} Hot Work Permits Require Review"
    
    def get_required_columns(self) -> List[str]:
        """Return required DataFrame columns for validation."""
        return [
            'event_id',
            'event_name',
            'vessel_id',
            'vessel_name',
            'vessel_email',
            'created_at',
            'status'
        ]
```

#### 7. Update Module Imports

**Edit `src/alerts/__init__.py`**:
```python
"""Alert implementations."""
from .hot_works_alert import HotWorksAlert  # ← CHANGE THIS

__all__ = ['HotWorksAlert']  # ← CHANGE THIS
```

#### 8. Register the Alert

**Edit `src/main.py`**:
```python
def register_alerts(scheduler: AlertScheduler, config: AlertConfig) -> None:
    """Register all alert implementations with the scheduler."""
    logger = logging.getLogger(__name__)
    
    # Register Hot Works Alert
    from src.alerts.hot_works_alert import HotWorksAlert  # ← CHANGE THIS
    hot_works_alert = HotWorksAlert(config)  # ← CHANGE THIS
    scheduler.register_alert(hot_works_alert.run)
    logger.info("[OK] Registered HotWorksAlert")  # ← CHANGE THIS
```

#### 9. Test the New Alert
```bash
# Test locally (if you have Python setup)
python -m src.main --dry-run --run-once

# Test in Docker
export UID=$(id -u) GID=$(id -g)
docker-compose build
docker-compose run --rm alerts python -m src.main --dry-run --run-once
```

#### 10. Deploy to Production
```bash
# Start container
docker-compose up -d

# Monitor logs
docker-compose logs -f alerts

# Check status
docker-compose ps

# View tracking file
docker-compose exec alerts cat data/sent_alerts.json | jq '.'
```

### Automated Script (Optional)

Create `scripts/create_new_alert_project.sh`:
```bash
#!/bin/bash
# Usage: ./scripts/create_new_alert_project.sh hot-works-alerts HotWorksAlert

set -e

PROJECT_NAME=$1
ALERT_CLASS_NAME=$2

if [ -z "$PROJECT_NAME" ] || [ -z "$ALERT_CLASS_NAME" ]; then
    echo "Usage: $0 <project-name> <AlertClassName>"
    echo "Example: $0 hot-works-alerts HotWorksAlert"
    exit 1
fi

echo "📦 Copying project template..."
cp -r . "../$PROJECT_NAME"
cd "../$PROJECT_NAME"

echo "🧹 Cleaning up old data..."
rm -rf data/*.json logs/*.log .git

echo "✏️  Updating alert class references..."
# macOS (BSD sed)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/VesselDocumentsAlert/$ALERT_CLASS_NAME/g" src/alerts/__init__.py
    sed -i '' "s/VesselDocumentsAlert/$ALERT_CLASS_NAME/g" src/main.py
    sed -i '' "s/new-vessel-certificates-app/$PROJECT_NAME-app/g" docker-compose.yml
else
    # Linux (GNU sed)
    sed -i "s/VesselDocumentsAlert/$ALERT_CLASS_NAME/g" src/alerts/__init__.py
    sed -i "s/VesselDocumentsAlert/$ALERT_CLASS_NAME/g" src/main.py
    sed -i "s/new-vessel-certificates-app/$PROJECT_NAME-app/g" docker-compose.yml
fi

echo "📝 Renaming alert file..."
ALERT_FILE=$(echo "$ALERT_CLASS_NAME" | sed 's/\([A-Z]\)/_\L\1/g' | sed 's/^_//')".py"
mv src/alerts/vessel_documents_alert.py "src/alerts/$ALERT_FILE"

echo "🎉 Initializing new git repository..."
git init

echo ""
echo "✅ New project created: $PROJECT_NAME"
echo ""
echo "📝 Next steps:"
echo "   1. cd ../$PROJECT_NAME"
echo "   2. Update .env with new configuration"
echo "   3. Create SQL query in queries/"
echo "   4. Implement alert logic in src/alerts/$ALERT_FILE"
echo "   5. Test: docker-compose run --rm alerts python -m src.main --dry-run --run-once"
echo "   6. Deploy: docker-compose up -d"
echo ""
```

Make executable:
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

# View logs (follow mode)
docker-compose logs -f alerts

# View last 100 lines
docker-compose logs --tail=100 alerts

# Stop the container
docker-compose down

# Restart after config changes
docker-compose restart alerts

# View container status
docker-compose ps
```

### Running Tests in Docker
```bash
# Run all tests
docker-compose run --rm alerts pytest tests/ -v

# Run with coverage
docker-compose run --rm alerts pytest tests/ --cov=src --cov-report=term

# Interactive shell
docker-compose run --rm alerts bash
```

### Docker Configuration

**`docker-compose.yml`**:
```yaml
services:
  alerts:
    build:
      context: .
      args:
        UID: ${UID:-1000}
        GID: ${GID:-1000}
    container_name: new-vessel-certificates-app
    env_file:
      - .env
    environment:
      SSH_KEY_PATH: /app/ssh_ubuntu_key
    volumes:
      - ./logs:/app/logs          # Logs persist on host
      - ./data:/app/data          # Tracking data persists on host
      - ./queries:/app/queries    # Mount queries for easy updates
      - ~/.ssh/your_key:/app/ssh_key:ro  # SSH key (read-only)
    restart: unless-stopped        # Auto-restart on failure
```

### Health Monitoring

The Docker container includes a healthcheck that verifies:
- Log file exists
- Log file was updated recently (within schedule frequency + 10 minutes)

**View health status**:
```bash
docker inspect --format='{{.State.Health.Status}}' new-vessel-certificates-app

# Possible values:
# - healthy: Container is working properly
# - unhealthy: Container has issues
# - starting: Health check hasn't completed yet
```

**View health check logs**:
```bash
docker inspect --format='{{json .State.Health}}' new-vessel-certificates-app | jq '.'
```

### Docker Commands Reference
```bash
# Build
export UID=$(id -u) GID=$(id -g)
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart alerts

# Logs (live)
docker-compose logs -f alerts

# Logs (last 100 lines)
docker-compose logs --tail=100 alerts

# Execute command
docker-compose exec alerts python -m src.main --run-once

# Shell access
docker-compose exec alerts bash

# Run tests
docker-compose run --rm alerts pytest tests/ -v

# Remove everything (including volumes)
docker-compose down -v
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
├── pytest.ini                    # Pytest configuration
├── README.md                     # This file
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── db_utils.py               # Database utilities (SSH tunnel, queries)
│   │
│   ├── core/                     # Core infrastructure (reusable)
│   │   ├── __init__.py
│   │   ├── base_alert.py         # Abstract base class for alerts (74% coverage)
│   │   ├── config.py             # Configuration management (98% coverage)
│   │   ├── tracking.py           # Event tracking system (71% coverage)
│   │   └── scheduler.py          # Scheduling logic (47% coverage)
│   │
│   ├── notifications/            # Notification handlers (reusable)
│   │   ├── __init__.py
│   │   ├── email_sender.py       # Email sending with SMTP (57% coverage)
│   │   └── teams_sender.py       # Teams integration (stub, 56% coverage)
│   │
│   ├── formatters/               # Email formatters (reusable)
│   │   ├── __init__.py
│   │   ├── html_formatter.py     # Rich HTML emails (91% coverage)
│   │   └── text_formatter.py     # Plain text emails (95% coverage)
│   │
│   ├── utils/                    # Utilities (reusable)
│   │   ├── __init__.py
│   │   ├── validation.py         # DataFrame validation (0% coverage)
│   │   └── image_utils.py        # Logo loading (0% coverage)
│   │
│   └── alerts/                   # Alert implementations (customized)
│       ├── __init__.py
│       └── vessel_documents_alert.py  # Current alert (88% coverage)
│
├── queries/                      # SQL queries (customized)
│   └── NewVesselCertificates.sql
│
├── media/                        # Company logos
│   ├── trans_logo_prominence_procreate_small.png
│   └── trans_logo_seatraders_procreate_small.png
│
├── data/                         # Runtime data (not in git)
│   └── sent_alerts.json          # Tracking file
│
├── logs/                         # Log files (not in git)
│   └── alerts.log
│
└── tests/                        # Unit tests (59% overall coverage)
    ├── conftest.py               # Shared fixtures
    ├── test_config.py            # Configuration tests
    ├── test_tracking.py          # Tracking tests
    ├── test_vessel_documents_alert.py  # Alert logic tests
    ├── test_formatters.py        # Formatter tests
    ├── test_email_sender.py      # Email sending tests
    ├── test_scheduler.py         # Scheduler tests
    └── test_integration.py       # End-to-end tests
```

### Code Quality Standards

**Before committing**:
```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src --cov-report=term

# Format code (if using black)
black src/ tests/

# Lint code (if using flake8)
flake8 src/ tests/
```

### Adding a New Alert to Same Project

**Not recommended**, but possible if you want multiple alerts in one container:

1. Create new alert class in `src/alerts/my_new_alert.py`
2. Update `src/alerts/__init__.py` to export it
3. Register in `src/main.py`'s `register_alerts()` function

**Note**: All alerts will run on the **same schedule** (SCHEDULE_FREQUENCY_HOURS).

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "No module named 'src'"
**Cause**: Running from wrong directory

**Solution**:
```bash
# Always run from project root
cd /path/to/vessel-documents-alerts
python -m src.main --dry-run --run-once
```

#### 2. Emails not sending in production mode
**Causes**:
- `DRY_RUN=True` in `.env` (check this first!)
- SMTP credentials incorrect
- Gmail blocking "less secure apps"
- Firewall blocking SMTP port

**Solution**:
```bash
# Check DRY_RUN setting
grep DRY_RUN .env

# Check SMTP settings
grep SMTP .env

# For Gmail: Use App Password (not regular password)
# 1. Enable 2FA: https://myaccount.google.com/security
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Use App Password in SMTP_PASS

# Test SMTP connection
telnet smtp.gmail.com 465
```

#### 3. "SSH key not found" error
**Cause**: SSH key path incorrect or not mounted in Docker

**Solution**:
```bash
# Check SSH key exists locally
ls -la ~/.ssh/your_key

# Update docker-compose.yml volume mount
volumes:
  - ~/.ssh/your_key:/app/ssh_ubuntu_key:ro  # ← Verify this path

# Update .env
SSH_KEY_PATH=/app/ssh_ubuntu_key  # Path inside container
```

#### 4. Database connection fails
**Causes**:
- SSH tunnel not working
- Database credentials incorrect
- Database not accessible from this host

**Solution**:
```bash
# Test SSH connection
ssh -i ~/.ssh/your_key user@host

# Test SSH tunnel manually
ssh -i ~/.ssh/your_key -L 5432:localhost:5432 user@host

# Test database connection (in another terminal)
psql -h localhost -p 5432 -U username -d database_name

# Check .env settings
grep -E "DB_|SSH_" .env
```

#### 5. "TypeError: Can't instantiate abstract class"
**Cause**: Alert class missing required methods

**Solution**: Implement all 6 required abstract methods:
```python
class MyAlert(BaseAlert):
    def fetch_data(self) -> pd.DataFrame: ...
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def route_notifications(self, df: pd.DataFrame) -> List[Dict]: ...
    def get_tracking_key(self, row: pd.Series) -> str: ...
    def get_subject_line(self, data: pd.DataFrame, metadata: Dict) -> str: ...
    def get_required_columns(self) -> List[str]: ...
```

#### 6. Timezone comparison errors
**Cause**: Mixing timezone-aware and timezone-naive datetimes

**Solution**: Always use timezone-aware datetimes:
```python
from zoneinfo import ZoneInfo

# Correct
tz = ZoneInfo(self.config.timezone)
cutoff = datetime.now(tz=tz)

# Localize database timestamps
df['created_at'] = df['created_at'].dt.tz_localize('UTC').dt.tz_convert(tz)
```

#### 7. Test failures
**Common test issues**:
```bash
# "No module named 'src.events_alerts'" (old test files)
# Solution: Delete old test files from previous versions

# "SSH key not found" in integration tests
# Solution: Tests mock the database connection, check test_integration.py

# "AttributeError: 'AlertScheduler' object has no attribute..."
# Solution: Check actual attribute name in src/core/scheduler.py
```

### Logging & Debugging
```bash
# View live logs (local)
tail -f logs/alerts.log

# View live logs (Docker)
docker-compose logs -f alerts

# View last 100 lines
tail -n 100 logs/alerts.log

# Search for errors
grep ERROR logs/alerts.log

# Search for specific vessel
grep "KNOSSOS" logs/alerts.log

# Check tracking file
cat data/sent_alerts.json | jq '.'

# Pretty-print tracking file
cat data/sent_alerts.json | python -m json.tool

# Count tracked events
cat data/sent_alerts.json | jq '.sent_events | length'
```

### Docker Debugging
```bash
# Container won't start
docker-compose logs alerts  # Check startup errors

# Container exits immediately
docker-compose ps  # Check exit code
docker-compose logs --tail=50 alerts

# Health check failing
docker inspect --format='{{json .State.Health}}' new-vessel-certificates-app | jq '.'

# File permission errors
# Make sure UID/GID are set correctly:
export UID=$(id -u) GID=$(id -g)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Network issues
docker-compose exec alerts ping google.com
docker-compose exec alerts curl -v smtp.gmail.com:465
```

### Testing Checklist

Before deploying to production:

- [ ] Dry-run completes without errors: `docker-compose run --rm alerts python -m src.main --dry-run --run-once`
- [ ] SQL query returns expected columns
- [ ] Email recipients configured correctly in `.env`
- [ ] CC recipients configured correctly per domain
- [ ] `DRY_RUN=False` in `.env` for production
- [ ] `DRY_RUN_EMAIL` contains valid test addresses
- [ ] Company logos exist in `media/` directory
- [ ] Tracking file updates after test run: `cat data/sent_alerts.json`
- [ ] No duplicates on second dry-run
- [ ] Docker build succeeds: `docker-compose build`
- [ ] Container starts: `docker-compose up -d`
- [ ] Container stays running: `docker-compose ps`
- [ ] Logs show successful execution: `docker-compose logs -f alerts`
- [ ] Health check passes: `docker inspect --format='{{.State.Health.Status}}' new-vessel-certificates-app`
- [ ] All tests pass: `docker-compose run --rm alerts pytest tests/ -v`

---

## 📚 Key Concepts

### Abstract Base Class Pattern

The `BaseAlert` class defines a **contract** that all alerts must follow:
```python
from abc import ABC, abstractmethod

class BaseAlert(ABC):
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """Fetch data from database."""
        pass
    
    @abstractmethod
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply alert-specific filtering logic."""
        pass
    
    # ... 4 more abstract methods ...
    
    def run(self) -> bool:
        """Complete workflow - already implemented!"""
        df = self.fetch_data()
        df_filtered = self.filter_data(df)
        # ... rest of workflow
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
AlertConfig dataclass instance created
  ↓
Passed to all components (alerts, formatters, senders)
  ↓
Accessed via self.config throughout application
```

### Tracking System
```
Event occurs in database
  ↓
Alert's fetch_data() retrieves it
  ↓
Check: Is tracking_key in sent_alerts.json?
  ↓
  ├─ NO (new event)
  │   ↓
  │   Send notification
  │   ↓
  │   Save tracking_key + timestamp to sent_alerts.json
  │
  └─ YES (already sent)
      ↓
      Check: Is event older than REMINDER_FREQUENCY_DAYS?
      ↓
      ├─ YES (old) → Send reminder + update timestamp
      └─ NO (recent) → Skip (already notified recently)
```

**When REMINDER_FREQUENCY_DAYS is blank/empty**:
- Events are **never removed** from `sent_alerts.json`
- Notifications are **never re-sent**
- System tracks events forever

### Email Routing Logic
```
1. Alert groups data by vessel_id
   ↓
2. For each vessel:
   - Get vessel_email (e.g., "vessel@vsl.prominencemaritime.com")
   - Extract domain: "prominencemaritime.com"
   ↓
3. Look up CC list in email_routing config:
   - Match "prominencemaritime.com" → PROMINENCE_EMAIL_CC_RECIPIENTS
   - Match "seatraders.com" → SEATRADERS_EMAIL_CC_RECIPIENTS
   - No match → Use INTERNAL_RECIPIENTS only
   ↓
4. Create email job:
   - TO: vessel_email
   - CC: matched CC list + INTERNAL_RECIPIENTS
```

### Dry-Run Safety Layers

**Three layers of protection**:

1. **`.env` DRY_RUN setting**: `DRY_RUN=True` redirects emails
2. **Command-line override**: `--dry-run` flag forces dry-run mode
3. **Runtime check**: `EmailSender` validates dry-run state before sending

**Example**:
```python
# In EmailSender.send()
if self.dry_run:
    raise RuntimeError("SAFETY CHECK FAILED: Dry-run mode is enabled!")

# In main.py
if args.dry_run or config.dry_run:
    config.email_sender = EmailSender(..., dry_run=True)
```

---

## 📞 Support

For questions or issues:

1. **Check this README** - Most answers are here
2. **Review logs**: `docker-compose logs -f alerts`
3. **Test in dry-run**: `docker-compose run --rm alerts python -m src.main --dry-run --run-once`
4. **Check tracking file**: `cat data/sent_alerts.json | jq '.'`
5. **Run tests**: `docker-compose run --rm alerts pytest tests/ -v`
6. **Contact**: data@prominencemaritime.com

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

# 3. Test dry-run
export UID=$(id -u) GID=$(id -g)
docker-compose build
docker-compose run --rm alerts python -m src.main --dry-run --run-once

# 4. Run tests
docker-compose run --rm alerts pytest tests/ -v

# 5. Deploy
docker-compose up -d

# 6. Monitor
docker-compose logs -f alerts

# 7. Check health
docker inspect --format='{{.State.Health.Status}}' <container-name>
```

**That's it! You now have a production-ready alert system.** 🚀

---

## 📖 Additional Resources

- **Python decouple docs**: https://pypi.org/project/python-decouple/
- **Pandas documentation**: https://pandas.pydata.org/docs/
- **Docker Compose docs**: https://docs.docker.com/compose/
- **Pytest documentation**: https://docs.pytest.org/
- **SSH tunnel guide**: https://www.ssh.com/academy/ssh/tunneling

---

*Last updated: November 2025*
