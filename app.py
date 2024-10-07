from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime
import mimetypes
from flask_socketio import disconnect, leave_room
from utils.utils import load_json_file, save_json_file, generate_unique_user_id
from utils.register import register_bp
from utils.message import handle_message, handle_typing
from utils.admin import admin_bp
from utils.commands import commands_bp
from utils.forgot_password import password_reset_bp
from utils.files import files_bp



app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Change this to a secure key in production
socketio = SocketIO(app)

app.register_blueprint(register_bp)
app.register_blueprint(admin_bp, url_prefix='/admin') 
app.register_blueprint(commands_bp)
app.register_blueprint(password_reset_bp)
app.register_blueprint(files_bp)


from flask_session import Session

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# In-memory store for active sessions (replace with a persistent solution for production)
active_sessions = {}


USER_ACCOUNTS_FILE = 'data/useraccounts.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'
BANNED_USERS_FILE = 'data/banned.json'
ADMINS_FILE = 'data/admins.json'
ADMIN_PASSWORD_FILE = 'data/admin_password.json'
CODES_FILE = 'data/codes.json'
TEMP_USER_ACCOUNTS_FILE = 'data/temp_useraccounts.json'

@app.before_request
def block_requests():
    # Define the paths to block
    blocked_paths = ['/data/user_accounts.json']
    
    if request.path in blocked_paths:
        return render_template('getclowned.html'), 403  # Render the blocked page with a 403 status code

@app.route('/data/user_accounts', methods=['POST'])
def handle_user_accounts():
    return jsonify({'message': 'Request successful'})

@app.before_request
def before_request():
    if request.is_secure:
        return  # Already HTTPS
    else:
        # Redirect to HTTPS
        return redirect(request.url.replace("http://", "https://"), code=301)

def require_verification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session and not is_verified(session['username']):
            flash('You must verify your email before accessing this page.')
            return redirect(url_for('verify', username=session['username']))
        return f(*args, **kwargs)
    return decorated_function

def is_verified(username):
    users = load_json_file(USER_ACCOUNTS_FILE)
    return users.get(username, {}).get('verified', False)


def load_json_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return {}

def save_json_file(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def is_admin(username):
    admins = load_json_file(ADMINS_FILE)
    return username in admins

def get_admin_password():
    """Retrieve the admin password from admin_password.json."""
    data = load_json_file(ADMIN_PASSWORD_FILE)
    return data.get('password', '')  # Default to an empty string if not found


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_authenticated' not in session:
        return redirect(url_for('admin_login'))

    # Load user accounts data
    users = load_json_file(USER_ACCOUNTS_FILE)
    return render_template('admin.html', users=users)

@app.route('/.well-known/pki-validation/<filename>')
def serve_verification_file(filename):
    return send_from_directory(os.path.join(app.static_folder, '.well-known/pki-validation'), filename)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate against admins.json
        if is_admin(username):
            # Check password
            if password == get_admin_password():
                session['admin_authenticated'] = True  # Set a session variable to indicate authentication
                session['username'] = username  # Store the username in the session
                return redirect(url_for('admin'))
            else:
                flash('Invalid admin password')
        else:
            flash('Invalid admin credentials')
    
    return render_template('admin_login.html')



@app.route('/admin_logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin_login'))

@app.route('/ban_user', methods=['POST'])
def ban_user():
    if 'username' not in session or not is_admin(session['username']):
        return jsonify({'message': 'Unauthorized'}), 403

    username = request.json.get('username')
    if not username:
        return jsonify({'message': 'No username provided'}), 400

    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return jsonify({'message': 'User not found'}), 404

    # Retrieve user details
    user_details = users[username]

    # Add to banned users
    banned_users = load_json_file(BANNED_USERS_FILE)
    banned_users[username] = {
        'password': user_details['password'],
        'email': user_details['email'],
        'registered_at': user_details['registered_at'],
        'public_ip': user_details.get('public_ip', '')
    }
    save_json_file(BANNED_USERS_FILE, banned_users)

    # Remove from user accounts
    del users[username]
    save_json_file(USER_ACCOUNTS_FILE, users)

    # Invalidate all sessions of the banned user
    if username in active_sessions:
        for session_id in active_sessions[username]:
            socketio.disconnect(sid=session_id)

    # Log out the banned user if they are currently logged in
    if username in session:
        session.pop(username, None)
        return jsonify({
            'message': 'User banned and deleted successfully',
            'redirect': '/logout'
        })

    return jsonify({
        'message': 'User banned and deleted successfully',
        'redirect': None
    })




@app.route('/')
def index():
    if 'username' in session:
        chat_logs = load_json_file(CHAT_LOGS_FILE)
        messages = chat_logs.get('messages', [])
        users = load_json_file(USER_ACCOUNTS_FILE)
        username = session['username']  # Get the username from the session
        return render_template('chat.html', messages=messages, users=list(users.keys()), username=username)
    return redirect(url_for('login'))


@app.route('/get_user_info')
def get_user_info():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username provided'}), 400

    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return jsonify({'error': 'User not found'}), 404

    # Example: sending username, email, and registration timestamp
    user_info = {
        'username': username,
        'email': users[username].get('email', 'N/A'),
        'registered_at': users[username].get('registered_at', 'N/A')
    }
    return jsonify(user_info)


@app.route('/userinfo-<username>')
def user_info(username):
    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return 'User not found', 404

    # Pass username to the template
    return render_template('userinfo.html', username=username)

failed_attempts = {}
verification_codes = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_json_file(USER_ACCOUNTS_FILE)
        user = users.get(username)

        if user is None:
            flash('User not found.')
            return render_template('login.html')

        if user['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))

        if username not in failed_attempts:
            failed_attempts[username] = {'count': 0, 'locked': False}

        failed_attempts[username]['count'] += 1

        if failed_attempts[username]['count'] >= 3:
            failed_attempts[username]['locked'] = True
            verification_code = str(random.randint(100000, 999999))
            verification_codes[username] = verification_code
            send_verification_email(user['email'], verification_code)
            flash('Too many failed attempts. A verification code has been sent to your email.')
            return redirect(url_for('locked_screen'))

        flash('Invalid credentials. Try again.')

    return render_template('login.html')



@app.route('/locked', methods=['GET', 'POST'])
def locked_screen():
    username = session.get('username')

    if request.method == 'POST':
        verification_code_input = request.form.get('verification_code')

        if username in verification_codes and verification_codes[username] == verification_code_input:
            failed_attempts[username] = {'count': 0, 'locked': False}
            return redirect(url_for('index'))
        else:
            flash('Incorrect verification code.')

    return render_template('locked.html')






        # Validate credentials
    if user and user['password'] == password:
            # Reset failed attempts after successful login
            failed_attempts[username] = {'count': 0, 'locked': False}
            session['username'] = username
            session_cookie_name = app.config.get('SESSION_COOKIE_NAME', 'session')
            session_id = session.get('_id', request.cookies.get(session_cookie_name))
            active_sessions[username] = session_id
            return redirect(url_for('index'))
    else:
            # Increment failed attempt counter
            if username not in failed_attempts:
                failed_attempts[username] = {'count': 0, 'locked': False}

            failed_attempts[username]['count'] += 1

            if failed_attempts[username]['count'] >= 4:
                failed_attempts[username]['locked'] = True
                verification_code = str(random.randint(100000, 999999))  # Generate random 6-digit code
                verification_codes[username] = verification_code
                if user and 'email' in user:
                    send_verification_email(user['email'], verification_code)
                flash('Too many failed attempts. A verification code has been sent to your email.')
                return render_template('login.html', requires_verification=True)
            else:
                flash('Invalid credentials. Try again.')

    return render_template('login.html', requires_verification=False)





def generate_unique_user_id(users):
    """Generate a unique 10-digit user ID that does not exist in the users data."""
    while True:
        user_id = str(random.randint(1000000000, 9999999999))
        if not any(user_id == user_data.get('user_id') for user_data in users.values()):
            return user_id
        
def send_verification_email(email, code):
    smtp_server = "smtp.fastmail.com"
    port = 587
    username = "thugverify11@fastmail.com"  # Your FastMail email address
    password = "28642x4c2p8q5d74"  # Your app-specific password
    subject = "THUG-CHAT Verification"
    body = f"Someone tried to login to your account too many times incorrectly. You must verify your account again to access it, here is your code: {code}"

    message = f'From: {username}\nTo: {email}\nSubject: {subject}\n\n{body}'

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, email, message)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)
   


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


@app.route('/logout')
def logout():
    username = session.get('username')
    if username in active_sessions:
        del active_sessions[username]
    session.pop('username', None)
    return redirect(url_for('login'))


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


import threading
import sys

def restart_app():
    while True:
        time.sleep(600)  # Sleep for 5 minutes
        os.execl(sys.executable, sys.executable, *sys.argv)

threading.Thread(target=restart_app, daemon=True).start()

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
