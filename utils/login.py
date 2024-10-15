import random
import smtplib
from flask import Blueprint, session, flash, redirect, url_for, render_template, request
from flask_wtf.csrf import CSRFProtect
import json
from .forms import LoginForm

login_bp = Blueprint('login', __name__)
csrf = CSRFProtect()

failed_attempts = {}

# Load USER_ACCOUNTS_FILE from paths.json
def load_user_accounts_file():
    with open('constants/paths.json') as f:
        paths = json.load(f)
        return paths['USER_ACCOUNTS_FILE']

USER_ACCOUNTS_FILE = load_user_accounts_file()

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        users = load_json_file(USER_ACCOUNTS_FILE)
        user = users.get(username)

        if user is None:
            flash('User not found.')
            return render_template('login.html', form=form)

        if user['password'] == password:
            session['username'] = username
            reset_failed_attempts(username)
            return redirect(url_for('index'))

        increment_failed_attempts(username)
        flash('Incorrect password. Please try again.')

    return render_template('login.html', form=form)  # Ensure form is passed here


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
