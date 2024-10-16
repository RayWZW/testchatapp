from flask import Blueprint, session, redirect, url_for, flash, request, render_template, jsonify
from flask_wtf.csrf import CSRFProtect
from utils.utils import load_json_file, save_json_file
import os
import json
import datetime
import secrets

admin_bp = Blueprint('admin', __name__)
csrf = CSRFProtect()

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'
BANNED_USERS_FILE = 'data/banned.json'
ADMINS_FILE = 'data/admins.json'
ADMIN_TOKEN_FILE = 'data/admin_token.json'

def generate_admin_token():
    return secrets.token_hex(16)

def load_admin_token():
    return load_json_file(ADMIN_TOKEN_FILE).get('token', None)

def save_admin_token(token):
    save_json_file(ADMIN_TOKEN_FILE, {'token': token})

def is_admin(username):
    admins = load_json_file(ADMINS_FILE)
    return username in admins

def authenticate_request():
    token = request.headers.get('X-Admin-Token')
    return token == load_admin_token()

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

    return jsonify({'message': 'User banned and deleted successfully', 'redirect': None})

def clear_user_messages(username):
    if 'username' not in session or not is_admin(session['username']) or not authenticate_request():
        return jsonify({'message': 'Unauthorized'}), 403

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    messages = chat_logs.get('messages', [])

    chat_logs['messages'] = [msg for msg in messages if msg['username'] != username]
    save_json_file(CHAT_LOGS_FILE, chat_logs)

    return jsonify({'message': 'Messages cleared successfully', 'redirect': None})

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

        if is_admin(username):
            if True:  # Replace with actual password validation
                session['admin_authenticated'] = True
                session['username'] = username
                token = generate_admin_token()
                save_admin_token(token)
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid admin password')
        else:
            flash('Invalid admin credentials')

    return render_template('admin_login.html')


@admin_bp.route('/logout', methods=['GET'])
def admin_logout():
    session.pop('username', None)
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/users/ban', methods=['POST'])
@csrf.exempt  # CSRF exemption if needed
def ban_user_route():
    username = request.json.get('username')
    return ban_user(username)

@admin_bp.route('/users/clear_messages', methods=['POST'])
@csrf.exempt  # CSRF exemption if needed
def clear_user_messages_route():
    username = request.json.get('username')
    return clear_user_messages(username)

CONTENT_FILE_PATH = os.path.join('utils', 'content.txt')

@admin_bp.route('/chats/clear_all', methods=['POST'])
@csrf.exempt  # CSRF exemption if needed
def clear_all_chats():
    if 'username' not in session or not is_admin(session['username']) or not authenticate_request():
        return jsonify({'message': 'Unauthorized'}), 403

    chat_logs = load_json_file(CHAT_LOGS_FILE)
    chat_logs['messages'] = []  # Clear all messages
    save_json_file(CHAT_LOGS_FILE, chat_logs)

    return jsonify({'message': 'All chat logs cleared successfully', 'redirect': None})
