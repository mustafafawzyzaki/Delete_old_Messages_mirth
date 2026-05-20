# Delete All Messages

Run the application in "delete all" mode to remove all messages from every Mirth Connect channel.

## Steps

1. Ensure the `.env` file has `DELETE_TYPE = all`
2. Verify `RESTART_CHANNEL` is set to `true` or `false` as desired
3. Run the script:

```bash
python delete_old_messages_mirth.py
```

## Expected Behavior

- Connects to Mirth Connect via REST API
- Retrieves all channel IDs
- Deletes all messages from each channel
- Optionally restarts running channels
- If `DB_MAINTENANCE_TYPE = yes`, shrinks and backs up the SQL Server database
