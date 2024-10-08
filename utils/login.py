import random
import smtplib
from flask import Blueprint, session, flash, redirect, url_for, render_template, request
import json

login_bp = Blueprint('login', __name__)

failed_attempts = {}

# Load USER_ACCOUNTS_FILE from paths.json
def load_user_accounts_file():
    with open('constants/paths.json') as f:
        paths = json.load(f)
        return paths['USER_ACCOUNTS_FILE']

USER_ACCOUNTS_FILE = load_user_accounts_file()

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_json_file(USER_ACCOUNTS_FILE)  # Ensure this function is defined elsewhere
        user = users.get(username)

        if user is None:
            flash('User not found.')
            return render_template('login.html')

        if user['password'] == password:
            session['username'] = username
            reset_failed_attempts(username)
            return redirect(url_for('index'))

        increment_failed_attempts(username)

    return render_template('login.html')


def increment_failed_attempts(username):
    if username not in failed_attempts:
        failed_attempts[username] = {'count': 0}

    failed_attempts[username]['count'] += 1

    flash('Invalid credentials. Try again.')


def reset_failed_attempts(username):
    if username in failed_attempts:
        failed_attempts[username] = {'count': 0}


def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}

def generate_unique_user_id(users):
    while True:
        user_id = str(random.randint(1000000000, 9999999999))
        if not any(user_id == user_data.get('user_id') for user_data in users.values()):
            return user_id
