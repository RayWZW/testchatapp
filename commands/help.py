import json
import os
import datetime
import time
from flask import Blueprint

CHAT_LOGS_FILE = "data/chatlogs.json"

help_bp = Blueprint('help', __name__)

def update_chat_logs(system_message):
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'r') as f:
            content = f.read()
            current_chat_logs = json.loads(content)

        current_chat_logs["messages"].append(system_message)

        with open(CHAT_LOGS_FILE, 'w') as f:
            json.dump(current_chat_logs, f)

def create_system_message(last_timestamp):
    response_timestamp = datetime.datetime.fromisoformat(last_timestamp) + datetime.timedelta(seconds=1)
    return {
        "timestamp": response_timestamp.isoformat(),
        "username": "SYSTEM",
        "message": "ALL COMMANDS ARE: .help, .usercount, and .clear"
    }

def watch_chat_logs():
    last_chat_logs = None

    while True:
        if os.path.exists(CHAT_LOGS_FILE):
            with open(CHAT_LOGS_FILE, 'r') as f:
                content = f.read()
                current_chat_logs = json.loads(content)

            # Check if chat logs are updated
            if last_chat_logs is None:
                last_chat_logs = current_chat_logs  # First-time initialization

            else:
                # If a new message is added since the last check
                if len(current_chat_logs.get("messages", [])) > len(last_chat_logs.get("messages", [])):
                    latest_message = current_chat_logs["messages"][-1]
                    latest_message_content = latest_message.get("message")
                    
                    # If the latest message is ".help"
                    if latest_message_content == ".help":
                        latest_timestamp = latest_message.get("timestamp")
                        system_message = create_system_message(latest_timestamp)
                        update_chat_logs(system_message)

                # Update the reference for future checks
                last_chat_logs = current_chat_logs

        time.sleep(1.4)  # Check every 1400 milliseconds

def start_chat_log_watcher():
    from threading import Thread
    watcher_thread = Thread(target=watch_chat_logs, daemon=True)
    watcher_thread.start()

# Start the watcher immediately when this module is imported
start_chat_log_watcher()
