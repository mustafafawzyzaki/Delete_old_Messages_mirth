import os
import datetime
import urllib3
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

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


def main():
    mirth_ip = os.getenv("MIRTH_IP")
    mirth_port = os.getenv("MIRTH_PORT")
    username = os.getenv("MIRTH_USERNAME")
    password = os.getenv("MIRTH_PASSWORD")
    restart_channel = os.getenv("RESTART_CHANNEL")
    delete_type = os.getenv("DELETE_TYPE")
    duration = os.getenv("DURATION")

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


if __name__ == "__main__":
    main()