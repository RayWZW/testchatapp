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
        "message": message
    }

def load_user_roles():
    """Load user roles from JSON file."""
    if os.path.exists(USER_ROLES_FILE):
        with open(USER_ROLES_FILE, 'r') as f:
            return json.load(f)
    return {}

def user_has_roles(username):
    """Check if a user has any of the allowed roles."""
    allowed_roles = {"moderator", "admin", "owner", "developer"}
    user_roles = load_user_roles()

    # Check if the user has roles in userroles.json
    user_info = user_roles.get(username, {})
    user_roles_set = set(user_info.get("additionalRoles", []))  # Assuming roles are stored in a list
    return not user_roles_set.isdisjoint(allowed_roles)

def purge_chat_logs(n):
    if os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'r') as f:
            current_chat_logs = json.load(f)

        # Get the current messages from the log
        messages = current_chat_logs.get("messages", [])

        # Ensure there are enough messages to purge
        if len(messages) >= n:
            # Remove the last N messages
            new_messages = messages[:-n]
        else:
            # If there are fewer messages, just clear them all
            new_messages = []

        # Update the chat logs
        current_chat_logs["messages"] = new_messages
        update_chat_logs(current_chat_logs)

def watch_chat_logs():
    last_chat_logs = None

    while True:
        if os.path.exists(CHAT_LOGS_FILE):
            with open(CHAT_LOGS_FILE, 'r') as f:
                content = f.read()
                current_chat_logs = json.loads(content)

            # First-time initialization of last_chat_logs
            if last_chat_logs is None:
                last_chat_logs = current_chat_logs

            else:
                # If new messages are added
                if len(current_chat_logs.get("messages", [])) > len(last_chat_logs.get("messages", [])):
                    latest_message = current_chat_logs["messages"][-1]
                    latest_message_content = latest_message.get("message")
                    username = latest_message.get("username")  # Get the username from the message

                    # Check if the latest message is a purge command
                    if latest_message_content.startswith(".purge"):
                        latest_timestamp = latest_message.get("timestamp")

                        # Check if the user has the allowed roles
                        if user_has_roles(username):
                            try:
                                # Extract the number of messages to purge from the command
                                n = int(latest_message_content.split(" ")[1])

                                # Purge the last N messages
                                purge_chat_logs(n)

                                # Create a system confirmation message
                                system_message = create_system_message(latest_timestamp, f"Purged the last {n} messages.")

                            except (IndexError, ValueError):
                                # If no number or invalid number was provided, send an error message
                                system_message = create_system_message(latest_timestamp, "Error: Invalid or missing number for purge command. Use .purge [number].")

                        else:
                            # User does not have permission
                            system_message = create_system_message(latest_timestamp, "Error: You do not have permission to use this command.")

                        # Reload chat logs after purging and append the system message (confirmation or error)
                        with open(CHAT_LOGS_FILE, 'r') as f:
                            refreshed_logs = json.load(f)

                        refreshed_logs["messages"].append(system_message)
                        update_chat_logs(refreshed_logs)

                # Update last_chat_logs reference
                last_chat_logs = current_chat_logs

        time.sleep(1.4)  # Check every 1400 milliseconds

def start_chat_log_watcher():
    from threading import Thread
    watcher_thread = Thread(target=watch_chat_logs, daemon=True)
    watcher_thread.start()

# Start the watcher immediately when this module is imported
start_chat_log_watcher()
