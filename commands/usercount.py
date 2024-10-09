import json
import os
import datetime
import time
from flask import Blueprint

CHAT_LOGS_FILE = "data/chatlogs.json"
USER_ACCOUNTS_FILE = "data/useraccounts.json"

usercount_bp = Blueprint('usercount', __name__)

def update_chat_logs(system_message):
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'r') as f:
            content = f.read()
            current_chat_logs = json.loads(content)

        current_chat_logs["messages"].append(system_message)

        with open(CHAT_LOGS_FILE, 'w') as f:
            json.dump(current_chat_logs, f)

def create_system_message(last_timestamp, user_count):
    response_timestamp = datetime.datetime.fromisoformat(last_timestamp) + datetime.timedelta(seconds=1)
    return {
        "timestamp": response_timestamp.isoformat(),
        "username": "SYSTEM",
        "message": f"CURRENT USER COUNT: {user_count}"
    }

def get_user_count():
    if os.path.exists(USER_ACCOUNTS_FILE):
        with open(USER_ACCOUNTS_FILE, 'r') as f:
            user_accounts = json.load(f)
            return len(user_accounts)  # Assuming user accounts are stored as a list
    return 0  # Return 0 if the file doesn't exist or is empty

def watch_chat_logs():
    last_chat_logs = None

    while True:
        if os.path.exists(CHAT_LOGS_FILE):
            with open(CHAT_LOGS_FILE, 'r') as f:
                content = f.read()
                current_chat_logs = json.loads(content)

            # Check for new messages
            if last_chat_logs != current_chat_logs:
                last_chat_logs = current_chat_logs

                # Check if the system message for ".usercount" already exists
                usercount_message_exists = any(
                    msg.get("message").startswith("CURRENT USER COUNT:")
                    for msg in current_chat_logs.get("messages", [])
                )

                user_count = get_user_count()  # Get user count from useraccounts.json

                for message in current_chat_logs.get("messages", []):
                    user_message = message.get("message")
                    message_timestamp = message.get("timestamp")

                    if user_message == ".usercount" and not usercount_message_exists:
                        # Create system message and update chat logs
                        system_message = create_system_message(message_timestamp, user_count)
                        update_chat_logs(system_message)

        time.sleep(1)  # Adjust the sleep time as needed

def start_chat_log_watcher():
    from threading import Thread
    watcher_thread = Thread(target=watch_chat_logs, daemon=True)
    watcher_thread.start()

# Start the watcher immediately when this module is imported
start_chat_log_watcher()
