from flask import Blueprint, session, redirect, url_for, flash, request, render_template, jsonify
from utils.utils import load_json_file, save_json_file
import os

admin_bp = Blueprint('admin', __name__)

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'
BANNED_USERS_FILE = 'data/banned.json'
ADMINS_FILE = 'data/admins.json'
ADMIN_PASSWORD_FILE = 'data/admin_password.json'

ADMIN_PASSWORD = '&89u98u543r89u453rereded'

def is_admin(username):
    admins = load_json_file(ADMINS_FILE)
    return username in admins

def get_admin_password():
    data = load_json_file(ADMIN_PASSWORD_FILE)
    return data.get('password', '')

def authenticate_request():
    password = request.headers.get('X-Admin-Password')
    return password == ADMIN_PASSWORD

def ban_user(username):
    if 'username' not in session or not is_admin(session['username']) or not authenticate_request():
        return jsonify({'message': 'Unauthorized'}), 403

    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return jsonify({'message': 'User not found'}), 404

    user_details = users[username]
    banned_users = load_json_file(BANNED_USERS_FILE)
    banned_users[username] = {
        'password': user_details['password'],
        'email': user_details['email'],
        'registered_at': user_details['registered_at'],
        'public_ip': user_details.get('public_ip', '')
    }
    save_json_file(BANNED_USERS_FILE, banned_users)

    del users[username]
    save_json_file(USER_ACCOUNTS_FILE, users)

    return jsonify({
        'message': 'User banned and deleted successfully',
        'redirect': None
    })

def clear_user_messages(username):
    if 'username' not in session or not is_admin(session['username']) or not authenticate_request():
        return jsonify({'message': 'Unauthorized'}), 403

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    messages = chat_logs.get('messages', [])

    chat_logs['messages'] = [msg for msg in messages if msg['username'] != username]

    save_json_file(CHAT_LOGS_FILE, chat_logs)

    return jsonify({
        'message': 'Messages cleared successfully',
        'redirect': None
    })

@admin_bp.route('/', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_authenticated' not in session:
        return redirect(url_for('admin.admin_login'))

    users = load_json_file(USER_ACCOUNTS_FILE)
    return render_template('admin.html', users=users)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if is_admin(username):
            if password == get_admin_password():
                session['admin_authenticated'] = True
                session['username'] = username
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid admin password')
        else:
            flash('Invalid admin credentials')
    
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/ban_user', methods=['POST'])
def ban_user_route():
    username = request.json.get('username')
    return ban_user(username)

@admin_bp.route('/clear_user_messages', methods=['POST'])
def clear_user_messages_route():
    username = request.json.get('username')
    return clear_user_messages(username)

@admin_bp.route('/clear_all_chats', methods=['POST'])
def clear_all_chats():
    if 'username' not in session or not is_admin(session['username']) or not authenticate_request():
        return jsonify({'message': 'Unauthorized'}), 403

    if os.path.exists(CHAT_LOGS_FILE):
        os.remove(CHAT_LOGS_FILE)

    return jsonify({'message': 'All chat logs cleared successfully'})
