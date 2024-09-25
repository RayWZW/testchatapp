from flask import session, request
from flask_socketio import emit, disconnect
from datetime import datetime, timedelta
from utils.utils import load_json_file, save_json_file
import threading
import re

BANNED_USERS_FILE = 'data/banned.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'
BLOCKED_WORDS_FILE = 'data/blockedwords.json'

message_times = {}
cooldown_users = {}

def load_blocked_words():
    blocked_words_data = load_json_file(BLOCKED_WORDS_FILE)
    return blocked_words_data.get('blocked_words', [])

BLOCKED_WORDS = load_blocked_words()

def replace_blocked_words(message):
    for word in BLOCKED_WORDS:
        pattern = re.escape(word)  # Escape the word to avoid regex special characters
        message = re.sub(pattern, '*' * len(word), message, flags=re.IGNORECASE)
    return message

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
    sanitized_message = replace_blocked_words(original_message)

    if sanitized_message != original_message:
        emit('error', {'error': 'Your message contained blocked content and has been sanitized.'}, room=request.sid)
    
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

    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    if 'file_url' in message:
        formatted_message = {
            'timestamp': timestamp,
            'username': username,
            'message': '',
            'file_url': message['file_url'],
            'file_type': message['file_type']
        }
    else:
        formatted_message = {
            'timestamp': timestamp,
            'username': username,
            'message': sanitized_message  # Use the sanitized message here
        }

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
