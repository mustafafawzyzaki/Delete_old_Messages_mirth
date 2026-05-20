# Delete Messages by Date Range

Run the application in "range" mode to delete messages older than a specified number of days from every Mirth Connect channel.

## Steps

1. Ensure the `.env` file has `DELETE_TYPE = range`
2. Set `DURATION` to the number of days (e.g., `7` deletes messages older than 7 days)
3. Run the script:

```bash
python delete_old_messages_mirth.py
```

## Expected Behavior

- Connects to Mirth Connect via REST API
- Retrieves all channel IDs
- For each channel, deletes messages with a date range from `1899-12-31` to `(today - DURATION days)`
- If `DB_MAINTENANCE_TYPE = yes`, shrinks and backs up the SQL Server database
