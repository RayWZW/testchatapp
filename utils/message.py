from flask import session, request
from flask_socketio import emit, disconnect
from datetime import datetime, timedelta
from utils.utils import load_json_file, save_json_file
import threading
import re  # Import the regex module

BANNED_USERS_FILE = 'data/banned.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'

message_times = {}
cooldown_users = {}

import re

def handle_message(message):
    username = session.get('username')

    if username is None:
        return

    banned_users = load_json_file(BANNED_USERS_FILE)
    if username in banned_users:
        emit('banned', {'error': 'You are banned from sending messages.'}, room=request.sid)
        disconnect()
        return

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

    if cooldown_users[username]:  # Prevent saving during cooldown
        return

    # Block specific tags
    if re.search(r'<(img|script|iframe|link|style|meta|object|embed|applet|form)[^>]*>', message, re.IGNORECASE):
        emit('error', {'error': 'Message contains forbidden HTML tags.'}, room=request.sid)
        return

    # Strip on-event attributes
    clean_message = re.sub(r'\s*on\w+=".*?"', '', message)  # Remove event handler attributes
    clean_message = re.sub(r'\s*on\w+=\'.*?\'', '', clean_message)  # Remove event handler attributes (single quotes)
    
    # Remove any remaining HTML tags
    clean_message = re.sub(r'<.*?>', '', clean_message)

    if not clean_message:  # Check if the message is empty after stripping HTML
        emit('error', {'error': 'Message contains only HTML and was rejected.'}, room=request.sid)
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
            'message': clean_message  # Use the cleaned message
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
