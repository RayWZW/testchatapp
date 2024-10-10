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

# Regex patterns to identify potentially harmful JavaScript code
MALICIOUS_JAVASCRIPT = re.compile(r'(javascript:|on\w+=|<script.*?>|<\/script>|eval\(|alert\(|document\.)', re.IGNORECASE)

def contains_javascript_code(message):
    return bool(MALICIOUS_JAVASCRIPT.search(message))

def remove_javascript_code(message):
    return re.sub(MALICIOUS_JAVASCRIPT, '', message)

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

    if is_file_message(original_message):
        formatted_message = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'username': username,
            'message': '',
            'file_url': message['file_url'],
            'file_type': message['file_type']
        }
    elif isinstance(original_message, str):
        if contains_javascript_code(original_message):
            emit('error', {'error': 'Your message contains harmful JavaScript and is not allowed.'}, room=request.sid)
            return

        # Remove any harmful JavaScript code
        sanitized_message = remove_javascript_code(original_message)

        formatted_message = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'username': username,
            'message': sanitized_message  # Store the sanitized message
        }
    else:
        return

    now = datetime.now()

    if username not in message_times:
        message_times[username] = []
    if username not in cooldown_users:
        cooldown_users[username] = False

    message_times[username] = [t for t in message_times[username] if now - t < timedelta(seconds=7)]

    if len(message_times[username]) >= 6:
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
    return isinstance(message, dict) and 'file_url' in message

def delete_message(timestamp):
    chat_logs = load_json_file(CHAT_LOGS_FILE)

    if 'messages' in chat_logs:
        chat_logs['messages'] = [msg for msg in chat_logs['messages'] if msg['timestamp'] != timestamp]
        save_json_file(CHAT_LOGS_FILE, chat_logs)

    emit('delete_message', timestamp, broadcast=True)
