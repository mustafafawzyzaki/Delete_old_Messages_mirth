# Database Maintenance

Run database shrink and backup after message deletion.

## Steps

1. Set `DB_MAINTENANCE_TYPE = yes` in `.env`
2. Configure SQL Server settings (`SQL_IP`, `SQL_PORT`, `DB_NAME`, etc.)
3. Run: `python delete_old_messages_mirth.py`

## Behavior

- Shrinks database via `DBCC SHRINKDATABASE`
- Creates a compressed full backup (`.bak`) in `BACKUP_PATH`
