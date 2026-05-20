# DEPLOYMENT.md — Build & Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Running from Source](#running-from-source)
4. [Building the Executable](#building-the-executable)
5. [Packaging for Distribution](#packaging-for-distribution)
6. [Deploying to a Server](#deploying-to-a-server)
7. [Scheduling with Windows Task Scheduler](#scheduling-with-windows-task-scheduler)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### On the Build Machine

| Requirement         | Version    | Notes                                    |
|---------------------|------------|------------------------------------------|
| Python              | 3.6+       | Tested with 3.10+                        |
| pip                 | Latest     | Comes with Python                        |
| SQL Server ODBC Driver | 17+     | Required for `pyodbc` to connect         |
| Network access      | —          | Must reach Mirth Connect API and SQL Server |

### On the Target Server

| Requirement                  | Notes                                             |
|------------------------------|---------------------------------------------------|
| Windows OS                   | Tested on Windows Server 2016/2019/2022           |
| SQL Server ODBC Driver 17+   | Required if `DB_MAINTENANCE_TYPE = yes`           |
| Network access to Mirth      | HTTPS access to Mirth Connect API port (default 8443) |
| Network access to SQL Server | TCP access to SQL Server port (default 1433)      |
| Administrator privileges     | Required for database operations                  |

---

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mustafafawzyzaki/Delete_old_Messages_mirth.git
cd Delete_old_Messages_mirth
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

```powershell
# PowerShell
.venv\Scripts\Activate.ps1

# Command Prompt
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Environment

Create a `.env` file in the project root (copy from the template below):

```env
# Mirth Connect Configuration
MIRTH_IP = 192.168.1.118
MIRTH_PORT = 8443
MIRTH_USERNAME = admin
MIRTH_PASSWORD = admin
RESTART_CHANNEL = true
DELETE_TYPE = all         # all or range
DURATION = 7

# SQL Server Settings
DB_MAINTENANCE_TYPE = no    # yes or no
SQL_IP = 192.168.1.121
SQL_PORT = 1433
DB_NAME = mirthdb
DB_USERNAME = sa
DB_PASSWORD = YourSecurePassword
BACKUP_PATH = C:\SQLBackups
```

> **⚠️ Security Note**: The `.env` file contains credentials. It is excluded from version control via `.gitignore`. Never commit it to the repository.

---

## Running from Source

```bash
python delete_old_messages_mirth.py
```

### Delete Type Options

| `DELETE_TYPE` | Behavior                                                          |
|---------------|-------------------------------------------------------------------|
| `all`         | Removes **all** messages from every channel, clears statistics    |
| `range`       | Removes messages **older than `DURATION` days** from every channel|

### Database Maintenance

Set `DB_MAINTENANCE_TYPE = yes` to enable post-deletion database maintenance:

1. **Shrink** — Executes `DBCC SHRINKDATABASE` to reclaim disk space
2. **Backup** — Creates a compressed full backup (`.bak`) with a timestamped filename

---

## Building the Executable

### Using the Command Line

```bash
pyinstaller --onefile --console --uac-admin delete_old_messages_mirth.py
```

### Using the Existing `.spec` File

```bash
pyinstaller delete_old_messages_mirth.spec
```

### Build Output

```
dist/
└── delete_old_messages_mirth.exe    # ~11 MB standalone executable
```

### Build Options Explained

| Flag          | Purpose                                                         |
|---------------|-----------------------------------------------------------------|
| `--onefile`   | Bundles everything into a single portable `.exe`                |
| `--console`   | Shows a console window for print output                        |
| `--uac-admin` | Requests Windows administrator privileges at launch            |

---

## Packaging for Distribution

After building, create a distribution package:

### 1. Create a Distribution Folder

```powershell
mkdir release
Copy-Item dist\delete_old_messages_mirth.exe release\
```

### 2. Create a Template `.env`

Create a `.env` file in the `release/` folder with placeholder values:

```env
# Mirth Connect Configuration
MIRTH_IP = <MIRTH_SERVER_IP>
MIRTH_PORT = 8443
MIRTH_USERNAME = <USERNAME>
MIRTH_PASSWORD = <PASSWORD>
RESTART_CHANNEL = true
DELETE_TYPE = all
DURATION = 7

# SQL Server Settings (optional)
DB_MAINTENANCE_TYPE = no
SQL_IP = <SQL_SERVER_IP>
SQL_PORT = 1433
DB_NAME = mirthdb
DB_USERNAME = <DB_USER>
DB_PASSWORD = <DB_PASSWORD>
BACKUP_PATH = C:\SQLBackups
```

### 3. Create a ZIP Archive

```powershell
Compress-Archive -Path release\* -DestinationPath delete_mirth_messages.zip
```

### Distribution Checklist

- [ ] `delete_old_messages_mirth.exe` is included
- [ ] `.env` template with placeholder values is included
- [ ] SQL Server ODBC Driver 17+ is installed on target machine
- [ ] Backup directory (`BACKUP_PATH`) exists on the SQL Server machine
- [ ] Firewall rules allow HTTPS to Mirth and TCP to SQL Server

---

## Deploying to a Server

### Step-by-Step

1. **Copy** the distribution archive (`.zip`) to the target server
2. **Extract** it to a permanent location, e.g., `C:\Tools\MirthMaintenance\`
3. **Edit** the `.env` file with the correct server IPs, credentials, and settings
4. **Test** by running the executable manually:

```powershell
cd C:\Tools\MirthMaintenance
.\delete_old_messages_mirth.exe
```

5. **Verify** output shows channels being processed and (if enabled) database maintenance completing

---

## Scheduling with Windows Task Scheduler

For automated, recurring maintenance, set up a Windows Scheduled Task:

### 1. Open Task Scheduler

```
taskschd.msc
```

### 2. Create a New Task

| Setting              | Value                                                    |
|----------------------|----------------------------------------------------------|
| **Name**             | `Mirth Message Cleanup`                                  |
| **Run as**           | A local admin account or service account                 |
| **Run whether or not user is logged on** | ✅ Enabled                      |
| **Run with highest privileges** | ✅ Enabled                                    |

### 3. Set the Trigger

| Setting     | Value                                          |
|-------------|------------------------------------------------|
| **Begin**   | On a schedule                                  |
| **Frequency**| Daily / Weekly (as needed)                    |
| **Time**    | Off-peak hours (e.g., `02:00 AM`)              |

### 4. Set the Action

| Setting       | Value                                                       |
|---------------|-------------------------------------------------------------|
| **Action**    | Start a program                                             |
| **Program**   | `C:\Tools\MirthMaintenance\delete_old_messages_mirth.exe`   |
| **Start in**  | `C:\Tools\MirthMaintenance`                                 |

> **Important**: The "Start in" directory must be set so that the `.env` file is found at runtime.

### 5. Recommended Settings

- **Stop the task if it runs longer than**: `1 hour`
- **If the task fails, restart every**: `5 minutes` (up to 3 attempts)

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ConnectionRefusedError` | Mirth Connect is unreachable | Verify `MIRTH_IP` and `MIRTH_PORT`, check firewall |
| `401 Unauthorized` | Wrong credentials | Check `MIRTH_USERNAME` and `MIRTH_PASSWORD` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Should not occur (SSL verification is disabled) | Ensure `urllib3` is installed |
| `pyodbc.InterfaceError` | ODBC driver not installed | Install [SQL Server ODBC Driver 17+](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) |
| `Login failed for user` | Wrong SQL credentials | Verify `DB_USERNAME` and `DB_PASSWORD` |
| `.env not found` | Missing or misplaced `.env` | Ensure `.env` is in the same directory as the `.exe` |
| `Backup directory does not exist` | `BACKUP_PATH` doesn't exist on SQL Server | Create the directory on the SQL Server machine |

### Checking Logs

The application prints all status messages to stdout. When running as a scheduled task, you can capture output:

```powershell
# Run with output logging
.\delete_old_messages_mirth.exe > maintenance_log.txt 2>&1
```

Update the Task Scheduler action to:
- **Program**: `cmd.exe`
- **Arguments**: `/c "C:\Tools\MirthMaintenance\delete_old_messages_mirth.exe >> C:\Tools\MirthMaintenance\logs\maintenance.log 2>&1"`

---

## Version History

| Version | Date       | Changes                                           |
|---------|------------|---------------------------------------------------|
| 1.0     | Initial    | Delete all messages from Mirth channels           |
| 1.1     | —          | Added date-range deletion support                 |
| 1.2     | —          | Added SQL Server shrink and backup functionality  |
