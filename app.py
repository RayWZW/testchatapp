from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime
from PIL import Image
import mimetypes
from flask_socketio import disconnect, leave_room
from utils.utils import load_json_file, save_json_file, require_verification, is_verified, is_admin, get_admin_password, resize_image, generate_unique_user_id
from utils.register import register_bp
from utils.message import handle_message, delete_message, handle_typing  # Adjusted import
from utils.admin import admin_bp
from utils.commands import commands_bp
from utils.forgot_password import password_reset_bp
from utils.files import files_bp
from routes.useraccounts import useraccounts_bp
from routes.uploadpfp import upload_pfp_bp
from routes.getchatlogs import getchatlogs_bp
from routes.accsettings import accsettings_bp
from routes.userinfo import userinfo_bp
from utils.login import login_bp
from routes.logout import logout_bp
from utils.roles import roles_bp
from utils.chatlog_updater import start_chatlog_watcher
from commands.usercount import usercount_bp
from commands.help import help_bp
from commands.purge import purge_bp
from utils.syncer import syncer_bp

app = Flask(__name__, static_folder='static')
app.secret_key = '98ew5-e9e5-ef545ew-we15ew15ew'  # Change this to a secure key in production
socketio = SocketIO(app)

app.register_blueprint(register_bp)
app.register_blueprint(admin_bp, url_prefix='/admin') 
app.register_blueprint(commands_bp)
app.register_blueprint(password_reset_bp)
app.register_blueprint(files_bp)
app.register_blueprint(useraccounts_bp)
app.register_blueprint(upload_pfp_bp)
app.register_blueprint(getchatlogs_bp)
app.register_blueprint(accsettings_bp)
app.register_blueprint(userinfo_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(roles_bp, url_prefix='/roles')
app.register_blueprint(usercount_bp)
app.register_blueprint(help_bp)
app.register_blueprint(purge_bp)
app.register_blueprint(syncer_bp)

import threading
watcher_thread = threading.Thread(target=start_chatlog_watcher, args=(socketio,))
watcher_thread.daemon = True
watcher_thread.start()

from flask_session import Session

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

active_sessions = {}


with open('constants/paths.json') as f:
    paths = json.load(f)

USER_ACCOUNTS_FILE = paths["USER_ACCOUNTS_FILE"]
CHAT_LOGS_FILE = paths["CHAT_LOGS_FILE"]
BANNED_USERS_FILE = paths["BANNED_USERS_FILE"]
ADMINS_FILE = paths["ADMINS_FILE"]
ADMIN_PASSWORD_FILE = paths["ADMIN_PASSWORD_FILE"]
CODES_FILE = paths["CODES_FILE"]
TEMP_USER_ACCOUNTS_FILE = paths["TEMP_USER_ACCOUNTS_FILE"]
PFP_FOLDER = paths["PFP_FOLDER"]
app.config['PFP_FOLDER'] = PFP_FOLDER

@app.before_request
def block_requests():
    # Define the paths to block
    blocked_paths = ['/data/useraccounts.json']
    
    if request.path in blocked_paths:
        return render_template('getclowned.html'), 403  # Render the blocked page with a 403 status code



@socketio.on('send_message')
def on_send_message(message):
    handle_message(message)  # Call the function from message.py

@socketio.on('send_command')  
def handle_send_command(data):
    username = data['username']  
    command = data['command']      
    response = handle_command(command, username)  
    emit('response', {'message': response})    

@socketio.on('delete_message_request')
def on_delete_message_request(timestamp):
    delete_message(timestamp)

@app.before_request
def before_request():
    if request.is_secure:
        return  # Already HTTPS
    else:
        # Redirect to HTTPS
        return redirect(request.url.replace("http://", "https://"), code=301)

@app.route('/')
def index():
    if 'username' in session:
        chat_logs = load_json_file(CHAT_LOGS_FILE)
        messages = chat_logs.get('messages', [])
        users = load_json_file(USER_ACCOUNTS_FILE)
        username = session['username']  # Get the username from the session
        return render_template('chat.html', messages=messages, users=list(users.keys()), username=username)
    return redirect(url_for('login.login'))

@app.route('/userinfo-<username>')
def user_info(username):
    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return 'User not found', 404

    # Pass username to the template
    return render_template('userinfo.html', username=username)
  


import smtplib
import random

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    return register(request)

@app.route('/verify/<username>', methods=['GET', 'POST'])
def verify_route(username):
    return verify(username, request)



@app.route('/tos')
def tos():
    return render_template('tos.html')



@app.route('/get_user_accounts')
def get_user_accounts():
    users = load_json_file(USER_ACCOUNTS_FILE)
    return jsonify(list(users.keys()))


@app.route('/get_messages')
def get_messages():
    chat_logs = load_json_file(CHAT_LOGS_FILE)
    messages = chat_logs.get('messages', [])
    return jsonify(messages)

@app.route('/user_count')
def user_count():
    users = load_json_file(USER_ACCOUNTS_FILE)
    count = len(users)
    return jsonify({'count': count})

from PIL import Image
import time


@app.route('/webhook/<int:id>', methods=['POST'])
def webhook(id):
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')
    # Process the received data as needed
    return jsonify({"status": "success", "id": id, "username": username, "message": message}), 200



from flask_socketio import SocketIO, emit
import time

# Dictionary to keep track of blocked IPs
blocked_ips = {}



@socketio.on('message')
def socket_handle_message(message):
    client_ip = request.remote_addr  # Get the client's IP address

    # Check if the client IP is blocked
    if client_ip in blocked_ips:
        block_time, block_until = blocked_ips[client_ip]
        if time.time() < block_until:  # If the block time is still active
            print(f"Message rejected from {client_ip}: Blocked until {block_until}.")
            emit('error', {'message': 'Your IP has been temporarily blocked due to spam. Please wait before sending more messages.'})
            return  # Reject the message

        # Remove the IP from the blocked list if the block duration has expired
        del blocked_ips[client_ip]

    # Check if the message is a string and its length exceeds 10,000 characters
    if isinstance(message, str) and len(message) > 20000:
        print(f"Message too long from {client_ip}, rejecting and blocking for 10 seconds.")
        # Block this IP for the next 10 seconds
        blocked_ips[client_ip] = (time.time(), time.time() + 10)
        emit('error', {'message': 'Your message is too long. You have been blocked for 10 seconds.'})
        return  # Reject the message

    handle_message(message)


@socketio.on('typing')
def socket_handle_typing():
    handle_typing()



base_dir = os.path.dirname(os.path.abspath(__file__))

# Define relative paths to your SSL files
ssl_context = (
    os.path.join(base_dir, "certificate.crt"),  # Certificate file
    os.path.join(base_dir, "private.key"),       # Private key file
)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=443, ssl_context=ssl_context)
