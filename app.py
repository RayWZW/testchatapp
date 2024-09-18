from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime
import mimetypes
from flask_socketio import disconnect, leave_room


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key in production
socketio = SocketIO(app)

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
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
        return render_template('chat.html', messages=messages, users=list(users.keys()))
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_json_file(USER_ACCOUNTS_FILE)
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            # Track the session ID
            session_id = session.get('_id', request.cookies.get(app.session_cookie_name))
            active_sessions[username] = session_id
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if len(username) < 6 or len(password) < 6:
            flash('Username and password must be at least 6 characters long')
            return render_template('register.html')

        users = load_json_file(USER_ACCOUNTS_FILE)
        banned_users = load_json_file(BANNED_USERS_FILE)

        if username in banned_users:
            flash('This user is banned and cannot register again')
            return render_template('register.html')

        if username in users:
            flash('Username already exists')
            return render_template('register.html')

        # Add new user details with timestamp and email
        users[username] = {
            'password': password,
            'email': email,
            'registered_at': timestamp
        }
        save_json_file(USER_ACCOUNTS_FILE, users)

        session['username'] = username
        return redirect(url_for('index'))

    return render_template('register.html')




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



@app.route('/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_url = url_for('download_file', filename=filename)
        file_type = mimetypes.guess_type(file_path)[0]  # Detect the MIME type
        return jsonify({'file_url': file_url, 'file_type': file_type})

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('message')
def handle_message(message):
    username = session.get('username', 'Anonymous')

    banned_users = load_json_file(BANNED_USERS_FILE)
    if username in banned_users:
        emit('banned', {'error': 'You are banned from sending messages.'}, room=request.sid)
        disconnect()
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
            'message': message
        }

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    if 'messages' not in chat_logs:
        chat_logs['messages'] = []
    chat_logs['messages'].append(formatted_message)
    save_json_file(CHAT_LOGS_FILE, chat_logs)

    emit('message', formatted_message, broadcast=True)



if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True))
