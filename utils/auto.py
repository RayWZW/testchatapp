from flask import Blueprint, request, jsonify
from utils.utils import load_json_file, save_json_file
import os
import json
from datetime import datetime
import time
import threading

auto_bp = Blueprint('auto', __name__)

# Load paths from constants
with open('constants/paths.json') as f:
    paths = json.load(f)

CHAT_LOGS_FILE = paths["CHAT_LOGS_FILE"]

# Define a secret token for authentication (this should be securely stored in production)
SYSTEM_TOKEN = os.environ.get('SYSTEM_TOKEN', '54er5-ew847ewr-we45we-ew451we')

def verify_token(request):
    """Helper function to verify the token from the request headers."""
    token = request.headers.get('Authorization')
    if not token or token != f"Bearer {SYSTEM_TOKEN}":
        return False
    return True

# Function to add help message to the chat logs
def add_help_message():
    chat_logs = load_json_file(CHAT_LOGS_FILE)
    messages = chat_logs.get('messages', [])
    help_message = {
        'username': 'SYSTEM',
        'message': 'Help: Here are some commands you can use: ...',
        'timestamp': datetime.now().isoformat()
    }
    messages.append(help_message)
    chat_logs['messages'] = messages
    save_json_file(CHAT_LOGS_FILE, chat_logs)

# Function to check for new messages in the chat logs
def monitor_chat_logs():
    last_checked_length = 0

    while True:
        chat_logs = load_json_file(CHAT_LOGS_FILE)
        messages = chat_logs.get('messages', [])

        # Check for new messages
        if len(messages) > last_checked_length:
            for msg in messages[last_checked_length:]:
                if msg['message'] == '.help':
                    add_help_message()  # Call the function to add help message
            
            last_checked_length = len(messages)

        time.sleep(5)  # Check every 5 seconds

@auto_bp.route('/add_message', methods=['POST'])
def add_message():
    """
    Adds a message to the chat logs as SYSTEM user. Requires token authentication.
    Request payload must contain:
    - message: the message content or command
    """
    if not verify_token(request):
        return jsonify({'error': 'Unauthorized: Invalid token.'}), 403

    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({'error': 'Message content is required.'}), 400

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    messages = chat_logs.get('messages', [])

    new_message = {
        'username': 'SYSTEM',
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

    messages.append(new_message)
    chat_logs['messages'] = messages
    save_json_file(CHAT_LOGS_FILE, chat_logs)

    return jsonify({'status': 'success', 'message': 'Message added successfully.'}), 200

@auto_bp.route('/edit_message', methods=['PUT'])
def edit_message():
    """
    Edits a message in the chat logs as SYSTEM user. Requires token authentication.
    Request payload must contain:
    - timestamp: the timestamp of the message to be edited
    - new_message: the new message content or command
    """
    if not verify_token(request):
        return jsonify({'error': 'Unauthorized: Invalid token.'}), 403

    data = request.get_json()
    timestamp = data.get('timestamp')
    new_message = data.get('new_message')

    if not timestamp or not new_message:
        return jsonify({'error': 'Timestamp and new message are required.'}), 400

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    messages = chat_logs.get('messages', [])

    for msg in messages:
        if msg['timestamp'] == timestamp:
            msg['message'] = new_message
            msg['username'] = 'SYSTEM'  # Ensure the username is "SYSTEM" after edit
            break
    else:
        return jsonify({'error': 'Message not found.'}), 404

    chat_logs['messages'] = messages
    save_json_file(CHAT_LOGS_FILE, chat_logs)

    return jsonify({'status': 'success', 'message': 'Message edited successfully.'}), 200

# Start the chat log monitoring in a separate thread
threading.Thread(target=monitor_chat_logs, daemon=True).start()
