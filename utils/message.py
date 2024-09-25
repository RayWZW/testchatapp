from flask import session, request
from flask_socketio import emit, disconnect
from datetime import datetime, timedelta
from utils.utils import load_json_file, save_json_file
import threading
import re

BANNED_USERS_FILE = 'data/banned.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'

message_times = {}
cooldown_users = {}

MALICIOUS_ATTRIBUTES = ['onerror', 'onclick', 'onload', 'onmouseover', 'onmouseout', 'onsubmit', 'onfocus', 'onblur']

def remove_malicious_attributes(message):
    for attr in MALICIOUS_ATTRIBUTES:
        message = re.sub(rf'\s*{attr}=["\'][^"\']*["\']', '', message, flags=re.IGNORECASE)
    return message

def contains_malicious_code(message):
    return bool(re.search(r'<[^>]+>', message))  # Check if there are any HTML tags in the message

def handle_message(message):
    username = session.get('username')

    if username is None:
        return

    banned_users = load_json_file(BANNED_USERS_FILE)
    if username in banned_users:
        emit('banned', {'error': 'You are banned from sending messages.'}, room=request.sid)
        disconnect()
        return

    original_message = message

    # Check if the message is a file message and skip HTML tag checks
    if not is_file_message(original_message) and isinstance(original_message, str):
        if contains_malicious_code(original_message):
            sanitized_message = remove_malicious_attributes(original_message)
            if sanitized_message != original_message:
                emit('error', {'error': 'Your message contained malicious attributes and has been sanitized.'}, room=request.sid)
                original_message = sanitized_message

    if is_file_message(original_message):
        formatted_message = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'username': username,
            'message': '',
            'file_url': message['file_url'],
            'file_type': message['file_type']
        }
    else:
        formatted_message = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'username': username,
            'message': original_message
        }

    now = datetime.now()

    if username not in message_times:
        message_times[username] = []

    if username not in cooldown_users:
        cooldown_users[username] = False

    message_times[username] = [t for t in message_times[username] if now - t < timedelta(seconds=7)]

    if len(message_times[username]) >= 10:
        if not cooldown_users[username]:
            emit('error', {'error': 'Slow down! You are sending messages too quickly.'}, room=request.sid)
            cooldown_users[username] = True
            threading.Timer(3, reset_cooldown, [username]).start()
        return

    message_times[username].append(now)

    if cooldown_users[username]:
        return

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    if 'messages' not in chat_logs:
        chat_logs['messages'] = []
    chat_logs['messages'].append(formatted_message)
    save_json_file(CHAT_LOGS_FILE, chat_logs)

    emit('message', formatted_message, broadcast=True)

def reset_cooldown(username):
    cooldown_users[username] = False

def handle_typing():
    username = session.get('username')
    if username is not None:
        emit('typing', {'username': username}, broadcast=True)

def is_file_message(message):
    return isinstance(message, dict) and 'file_url' in message  # Ensure it is a dict and contains 'file_url'
