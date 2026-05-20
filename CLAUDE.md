# CLAUDE.md — Project Instructions

## Project Overview

**Delete Old Messages Mirth** is a Python-based automation utility for managing Mirth Connect message retention and SQL Server database maintenance. It connects to a Mirth Connect instance via its REST API, retrieves all configured channels, and bulk-deletes messages — either all messages or those older than a configurable number of days. Optionally, it performs post-deletion SQL Server database maintenance (shrink + full backup).

This tool is designed for **healthcare IT environments** running [Mirth Connect](https://www.nextgen.com/products-and-services/integration-engine) (also known as NextGen Connect / Open Integration Engine) where message accumulation leads to performance degradation and disk space exhaustion.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              delete_old_messages_mirth.py             │
│                                                      │
│  ┌─────────────────┐    ┌──────────────────────────┐ │
│  │   .env (config)  │───▶│         main()           │ │
│  └─────────────────┘    │                          │ │
│                          │  1. get_all_channels()   │ │
│                          │  2. delete messages      │ │
│                          │  3. shrink_db()          │ │
│                          │  4. backup_db()          │ │
│                          └──────────────────────────┘ │
│                                  │           │        │
│                    ┌─────────────┘           │        │
│                    ▼                         ▼        │
│         ┌──────────────────┐    ┌──────────────────┐ │
│         │  Mirth Connect   │    │   SQL Server     │ │
│         │  REST API        │    │   (pyodbc)       │ │
│         │  (HTTPS)         │    │                  │ │
│         └──────────────────┘    └──────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## File Structure

```
Delete_old_Messages/
├── .claude/                          # Claude Code configuration
│   ├── settings.json                 # Permissions and tool access
│   └── commands/                     # Slash commands for common tasks
│       ├── delete_all_messages.md
│       ├── delete_range_messages.md
│       ├── build_exe.md
│       └── db_maintenance.md
├── .env                              # Runtime configuration (not in git)
├── .gitignore                        # Git ignore rules
├── delete_old_messages_mirth.py      # Main application script
├── delete_old_messages_mirth.spec    # PyInstaller build spec
├── requirements.txt                  # Python dependencies
├── dist/                             # Build output (not in git)
│   ├── delete_old_messages_mirth.exe # Standalone executable
│   ├── delete_mirth_messages.zip     # Distribution archive
│   └── .env                          # Template env for distribution
├── CLAUDE.md                         # This file — project context
└── DEPLOYMENT.md                     # Build and deployment guide
```

---

## Core Functions

### `get_all_channels()`
Queries the Mirth Connect REST API (`GET /api/channels`) and parses the XML response to extract all channel IDs.

### `delete_messages_in_channel()`
Calls `DELETE /api/channels/_removeAllMessages` to remove **all** messages from a specific channel. Supports optional channel restart.

### `delete_message_based_specific_range()`
Calls `DELETE /api/channels/{channelId}/messages` with `startDate` and `endDate` parameters to delete messages within a date range. The start date is fixed to `1899-12-31` and the end date is calculated as `today - DURATION days`.

### `shrink_db()`
Connects to SQL Server via `pyodbc` and executes `DBCC SHRINKDATABASE` to reclaim unused space after message deletion.

### `backup_db()`
Performs a full compressed backup of the SQL Server database to a timestamped `.bak` file using `BACKUP DATABASE ... TO DISK`.

---

## Configuration

All configuration is managed via a `.env` file located alongside the script or executable.

### Mirth Connect Settings

| Variable           | Description                                    | Example            |
|--------------------|------------------------------------------------|--------------------|
| `MIRTH_IP`         | IP address of the Mirth Connect server         | `192.168.1.118`    |
| `MIRTH_PORT`       | HTTPS API port                                 | `8443`             |
| `MIRTH_USERNAME`   | API authentication username                    | `admin`            |
| `MIRTH_PASSWORD`   | API authentication password                    | `admin`            |
| `RESTART_CHANNEL`  | Restart channels after deletion (`true`/`false`)| `true`            |
| `DELETE_TYPE`      | Deletion mode: `all` or `range`                | `all`              |
| `DURATION`         | Days to retain when using `range` mode         | `7`                |

### SQL Server Settings

| Variable              | Description                                    | Example             |
|-----------------------|------------------------------------------------|---------------------|
| `DB_MAINTENANCE_TYPE` | Enable DB maintenance: `yes` or `no`           | `no`                |
| `SQL_IP`              | SQL Server IP address                          | `192.168.1.121`     |
| `SQL_PORT`            | SQL Server port                                | `1433`              |
| `DB_NAME`             | Database name                                  | `mirthdb`           |
| `DB_USERNAME`         | SQL authentication username                    | `sa`                |
| `DB_PASSWORD`         | SQL authentication password                    | `password`          |
| `BACKUP_PATH`         | Directory for backup files (on SQL Server)     | `C:\SQLBackups`     |

---

## Dependencies

| Package          | Purpose                                      |
|------------------|----------------------------------------------|
| `requests`       | HTTP client for Mirth Connect REST API calls |
| `python-dotenv`  | Load `.env` file into environment variables  |
| `pyodbc`         | SQL Server database connectivity (ODBC)      |
| `pyinstaller`    | Build standalone Windows executables         |

---

## Key Technical Details

- **SSL Verification Disabled**: The script disables SSL verification (`verify=False`) and suppresses `InsecureRequestWarning` because Mirth Connect typically uses self-signed certificates.
- **Mirth API Authentication**: Uses HTTP Basic Auth via the `auth=` parameter in `requests`.
- **XML Parsing**: Mirth Connect API returns XML; the script uses `xml.etree.ElementTree` to parse channel IDs.
- **SQL Server Autocommit**: Both `shrink_db` and `backup_db` use `autocommit=True` because `DBCC` and `BACKUP` commands cannot run inside transactions.
- **UAC Admin**: The PyInstaller spec includes `uac_admin=True` to request elevated privileges on Windows.
- **Date Format**: Date strings use the format `%Y-%m-%dT00:00:00.000-0200` with a fixed timezone offset.

---

## Development Workflow

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python delete_old_messages_mirth.py

# Build standalone executable
pyinstaller --onefile --console --uac-admin delete_old_messages_mirth.py
```

---

## Coding Conventions

- **Python 3.6+** compatibility
- **No classes** — the codebase uses pure functions and a `main()` entry point
- **Environment-driven configuration** — all settings come from `.env`, no hardcoded values in the script
- **Print-based logging** — uses `print()` for status output (no logging framework)
- **f-strings** throughout for string formatting
