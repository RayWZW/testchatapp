import json
import os
import datetime
import time
from flask import Blueprint

CHAT_LOGS_FILE = "data/chatlogs.json"
PFP_DIRECTORY = "static/pfps/"  # Directory where profile pictures are stored

download_pfp_bp = Blueprint('download_pfp', __name__)

def update_chat_logs(system_message):
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'r') as f:
            content = f.read()
            current_chat_logs = json.loads(content)

        current_chat_logs["messages"].append(system_message)

        with open(CHAT_LOGS_FILE, 'w') as f:
            json.dump(current_chat_logs, f)

def create_download_message(last_timestamp, username, pfp_url):
    response_timestamp = datetime.datetime.fromisoformat(last_timestamp) + datetime.timedelta(seconds=1)
    return {
        "timestamp": response_timestamp.isoformat(),
        "username": "SYSTEM",
        "message": (
            f"<iframe src='{pfp_url}' width='500' height='430' frameborder='0' allowfullscreen title='Profile Picture'></iframe>"
        )
    }

def get_user_profile_picture_url(username):
    # List all files in the profile picture directory
    for filename in os.listdir(PFP_DIRECTORY):
        if filename.lower() == f"{username.lower()}.png":  # Check if filename matches
            return f"/{PFP_DIRECTORY}{filename}"  # Serve it from the static directory
    return None

def watch_chat_logs():
    last_chat_logs = None

    while True:
        if os.path.exists(CHAT_LOGS_FILE):
            with open(CHAT_LOGS_FILE, 'r') as f:
                content = f.read()
                current_chat_logs = json.loads(content)

            if last_chat_logs is None:
                last_chat_logs = current_chat_logs

            else:
                if len(current_chat_logs.get("messages", [])) > len(last_chat_logs.get("messages", [])):
                    latest_message = current_chat_logs["messages"][-1]
                    latest_message_content = latest_message.get("message")
                    
                    # Check if the latest message is the download command
                    if latest_message_content.startswith(".downloadpfp"):
                        parts = latest_message_content.split()
                        if len(parts) == 2:
                            username = parts[1].strip()  # Trim any whitespace
                            latest_timestamp = latest_message.get("timestamp")
                            pfp_url = get_user_profile_picture_url(username)

                            if pfp_url:
                                system_message = create_download_message(latest_timestamp, username, pfp_url)
                            else:
                                system_message = create_download_message(latest_timestamp, username, "Profile picture not found.")

                            update_chat_logs(system_message)

                last_chat_logs = current_chat_logs

        time.sleep(1.4)  # Check every 1400 milliseconds

def start_chat_log_watcher():
    from threading import Thread
    watcher_thread = Thread(target=watch_chat_logs, daemon=True)
    watcher_thread.start()

# Start the watcher immediately when this module is imported
start_chat_log_watcher()
