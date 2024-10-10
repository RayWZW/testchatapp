import json
import os
import time
from threading import Thread
from flask import Blueprint

USER_ACCOUNTS_FILE = "data/useraccounts.json"
USER_ROLES_FILE = "data/userroles.json"

syncer_bp = Blueprint('syncer', __name__)

def load_json_file(file_path):
    """Loads a JSON file and returns the content."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def update_user_accounts_with_roles():
    """Syncs the userroles.json with useraccounts.json, updating user accounts with their roles."""
    user_accounts = load_json_file(USER_ACCOUNTS_FILE)
    user_roles = load_json_file(USER_ROLES_FILE)

    for username in user_accounts:
        if username in user_roles:
            # Update roles if the user is found in userroles.json
            user_accounts[username]['roles'] = user_roles[username]['additionalRoles']
        else:
            # Remove roles if the user is not found in userroles.json
            user_accounts[username].pop('roles', None)

    with open(USER_ACCOUNTS_FILE, 'w') as f:
        json.dump(user_accounts, f, indent=4)

def sync_roles_periodically():
    """Runs the sync function every 100 milliseconds."""
    while True:
        update_user_accounts_with_roles()
        time.sleep(0.1)  # Sleep for 100 milliseconds

# Start the synchronization in a background thread
def start_syncer():
    sync_thread = Thread(target=sync_roles_periodically, daemon=True)
    sync_thread.start()

@syncer_bp.route('/sync_roles', methods=['POST'])
def sync_roles():
    """Endpoint to sync user roles."""
    update_user_accounts_with_roles()
    return {"message": "User accounts have been successfully updated with roles."}, 200

# Call this function to start the background sync when the blueprint is registered
start_syncer()
