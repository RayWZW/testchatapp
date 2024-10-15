import json
import os
import datetime
import time
from flask import Blueprint

CHAT_LOGS_FILE = "data/chatlogs.json"
USER_ROLES_FILE = "data/userroles.json"

purge_bp = Blueprint('purge', __name__)

def update_chat_logs(new_chat_logs):
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'w') as f:
            json.dump(new_chat_logs, f, indent=4)

def create_system_message(last_timestamp, message):
    response_timestamp = datetime.datetime.fromisoformat(last_timestamp) + datetime.timedelta(seconds=1)
    return {
        "timestamp": response_timestamp.isoformat(),
        "username": "SYSTEM",
        "message": message,
        "system_message": True,  # Mark this message as a system message for easy tracking
        "added_time": time.time()  # Record when the system message was added
    }

def load_user_roles():
    if os.path.exists(USER_ROLES_FILE):
        with open(USER_ROLES_FILE, 'r') as f:
            return json.load(f)
    return {}

def remove_system_messages():
    """Remove system messages that are older than 2 seconds."""
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'r') as f:
            current_chat_logs = json.load(f)
        current_time = time.time()
        messages = current_chat_logs.get("messages", [])
        updated_messages = [msg for msg in messages if not (msg.get("system_message") and current_time - msg.get("added_time", 0) > 2)]
        if len(updated_messages) != len(messages):
            current_chat_logs["messages"] = updated_messages
            update_chat_logs(current_chat_logs)

def user_has_roles(username):
    allowed_roles = {"moderator", "admin", "owner", "developer"}
    user_roles = load_user_roles()
    user_info = user_roles.get(username, {})
    user_roles_set = set(user_info.get("additionalRoles", []))
    return not user_roles_set.isdisjoint(allowed_roles)

def purge_chat_logs(n, username):
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'r') as f:
            current_chat_logs = json.load(f)
        messages = current_chat_logs.get("messages", [])

        # Filter out messages that are system messages or contain the purge command
        filtered_messages = [msg for msg in messages if not (msg.get("system_message") or msg.get("message").startswith(".purge"))]

        if len(filtered_messages) >= n:
            new_messages = filtered_messages[:-n]  # Purge the specified number of messages
        else:
            new_messages = []
        
        current_chat_logs["messages"] = new_messages
        update_chat_logs(current_chat_logs)

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
                    username = latest_message.get("username")

                    if latest_message_content.startswith(".purge"):
                        latest_timestamp = latest_message.get("timestamp")
                        if user_has_roles(username):
                            try:
                                n = int(latest_message_content.split(" ")[1])
                                purge_chat_logs(n, username)  # Pass username to purge function
                                system_message = create_system_message(latest_timestamp, f"Purged the last {n} messages.")
                            except (IndexError, ValueError):
                                system_message = create_system_message(latest_timestamp, "Error: Invalid or missing number for purge command. Use .purge [number].")
                        else:
                            system_message = create_system_message(latest_timestamp, "Error: You do not have permission to use this command.")

                        with open(CHAT_LOGS_FILE, 'r') as f:
                            refreshed_logs = json.load(f)
                        refreshed_logs["messages"].append(system_message)
                        update_chat_logs(refreshed_logs)

                last_chat_logs = current_chat_logs

        time.sleep(1.4)
        remove_system_messages()


def start_chat_log_watcher():
    from threading import Thread
    watcher_thread = Thread(target=watch_chat_logs, daemon=True)
    watcher_thread.start()

start_chat_log_watcher()
 