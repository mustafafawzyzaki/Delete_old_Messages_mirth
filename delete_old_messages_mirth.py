import os
import datetime
import urllib3
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import pyodbc 

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_channels(mirth_connect_ip, mirth_connect_port, mirth_connect_username, mirth_connect_password):
    url = requests.get(
        f"https://{mirth_connect_ip}:{mirth_connect_port}/api/channels",
        headers={"Accept": "application/xml", "X-Requested-With": "OpenAPI"},
        verify=False,
        auth=(mirth_connect_username, mirth_connect_password),
    )
    result = url.text
    channel_info = []

    root = ET.fromstring(result)
    for channel in root.findall("channel"):
        channel_info.append(channel.find("id").text)

    return channel_info

def delete_messages_in_channel(
    mirth_connect_ip,
    mirth_connect_port,
    mirth_connect_username,
    mirth_connect_password,
    channel_id,
    restart_channel,
):
    result = requests.delete(
        f"https://{mirth_connect_ip}:{mirth_connect_port}/api/channels/_removeAllMessages",
        params={
            "channelId": channel_id,
            "restartRunningChannels": restart_channel,
            "clearStatistics": "true",
        },
        headers={"accept": "application/xml", "X-Requested-With": "OpenAPI"},
        verify=False,
        auth=(mirth_connect_username, mirth_connect_password),
    )
    return result.text

def delete_message_based_specific_range(
    mirth_connect_ip,
    mirth_connect_port,
    mirth_connect_username,
    mirth_connect_password,
    channel_id,
    duration,
):
    start_date = "1899-12-31T00:00:00.000-0200"
    enddate = (datetime.datetime.now() - datetime.timedelta(days=duration)).strftime(
        "%Y-%m-%dT00:00:00.000-0200"
    )
    url = requests.delete(
        f"https://{mirth_connect_ip}:{mirth_connect_port}/api/channels/{channel_id}/messages",
        params={"startDate": start_date, "endDate": enddate},
        headers={"Accept": "application/xml", "X-Requested-With": "OpenAPI"},
        verify=False,
        auth=(mirth_connect_username, mirth_connect_password),
    )
    return url.text, url.status_code, start_date, enddate

def shrink_db(sql_ip, sql_port, db_name, db_username, db_password):
    """Shrink the SQL Server database to reclaim unused space."""
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={sql_ip},{sql_port};"
        f"DATABASE={db_name};"
        f"UID={db_username};"
        f"PWD={db_password}"
    )
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    print(f"Shrinking database '{db_name}'...")
    cursor.execute(f"DBCC SHRINKDATABASE ([{db_name}])")
    print(f"Database '{db_name}' shrunk successfully.")
    cursor.close()
    conn.close()

def backup_db(sql_ip, sql_port, db_name, db_username, db_password, backup_path):
    """Perform a full backup of the SQL Server database."""
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={sql_ip},{sql_port};"
        f"DATABASE={db_name};"
        f"UID={db_username};"
        f"PWD={db_password}"
    )
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_path, f"{db_name}_{timestamp}.bak")
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    print(f"Backing up database '{db_name}' to '{backup_file}'...")
    cursor.execute(
        f"BACKUP DATABASE [{db_name}] TO DISK = N'{backup_file}' "
        f"WITH FORMAT, INIT, NAME = N'{db_name} Full Backup'"
    )
    # Consume all result sets to ensure the backup completes
    while cursor.nextset():
        pass
    print(f"Backup completed: {backup_file}")
    cursor.close()
    conn.close()

def main():
    # Mirth Connect settings
    mirth_ip = os.getenv("MIRTH_IP")
    mirth_port = os.getenv("MIRTH_PORT")
    username = os.getenv("MIRTH_USERNAME")
    password = os.getenv("MIRTH_PASSWORD")
    restart_channel = os.getenv("RESTART_CHANNEL")
    delete_type = os.getenv("DELETE_TYPE")
    duration = os.getenv("DURATION")

    # SQL Server settings
    db_maintenance_type = os.getenv("DB_MAINTENANCE_TYPE")
    sql_ip = os.getenv("SQL_IP")
    sql_port = os.getenv("SQL_PORT", "1433")
    db_name = os.getenv("DB_NAME")
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    backup_path = os.getenv("BACKUP_PATH", r"C:\SQLBackups")


    # --- Step 1: Delete old messages from Mirth channels ---
    channel_ids = get_all_channels(mirth_ip, mirth_port, username, password)

    for channel_id in channel_ids:
        if delete_type == "all":
            delete_messages_in_channel(
                mirth_ip, mirth_port, username, password, channel_id, restart_channel
            )
            print(f"the channel data {channel_id} was removed")
        elif delete_type == "range":
            duration = int(os.getenv("DURATION"))
            delete_message_based_specific_range(
                mirth_ip, mirth_port, username, password, channel_id, duration
            )
            print(f"the channel data {channel_id} was removed")

    if db_maintenance_type == "yes":       
        # --- Step 2: Shrink the SQL Server database ---
        if sql_ip and db_name:
            shrink_db(sql_ip, sql_port, db_name, db_username, db_password)

        # --- Step 3: Backup the SQL Server database ---
        if sql_ip and db_name:
            backup_db(sql_ip, sql_port, db_name, db_username, db_password, backup_path)


if __name__ == "__main__":
    main()