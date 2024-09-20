from flask import Blueprint, flash, redirect, url_for, session, render_template, request
from datetime import datetime
import os
import random
import smtplib
from utils.utils import load_json_file, save_json_file, generate_unique_user_id

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
TEMP_USER_ACCOUNTS_FILE = 'data/temp_useraccounts.json'
BANNED_USERS_FILE = 'data/banned.json'

register_bp = Blueprint('register', __name__)

def send_verification_email(email, code):
    sender_email = "ryantraven14232@outlook.com"
    sender_password = "Mickey2021"
    subject = "THUG-CHAT Verification"
    body = f"Your verification code is: {code}"

    with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(sender_email, email, message)

@register_bp.route('/register', methods=['GET', 'POST'])
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

        if any(user['email'] == email for user in users.values()):
            flash('An account with this email already exists')
            return render_template('register.html')

        verification_code = random.randint(100000, 999999)
        send_verification_email(email, verification_code)

        temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE) if os.path.exists(TEMP_USER_ACCOUNTS_FILE) else {}
        temporary_users[username] = {
            'password': password,
            'email': email,
            'registered_at': timestamp,
            'verified': False,
            'verification_code': verification_code,
            'verification_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        save_json_file(TEMP_USER_ACCOUNTS_FILE, temporary_users)
        return redirect(url_for('register.verify', username=username))

    return render_template('register.html')

@register_bp.route('/verify/<username>', methods=['GET', 'POST'])
def verify(username):
    users = load_json_file(USER_ACCOUNTS_FILE)
    temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE)
    user = temporary_users.get(username)

    if request.method == 'POST':
        code_entered = request.form['code']
        current_time = datetime.now()
        verification_time = datetime.strptime(user['verification_time'], '%Y-%m-%d %H:%M:%S')

        if user and str(user['verification_code']) == code_entered:
            if (current_time - verification_time).total_seconds() <= 600:
                user_id = generate_unique_user_id(users)
                user['verified'] = True
                user['user_id'] = user_id
                users[username] = {
                    'user_id': user_id,
                    'password': user['password'],
                    'email': user['email'],
                    'registered_at': user['registered_at'],
                    'verified': True
                }
                save_json_file(USER_ACCOUNTS_FILE, users)
                os.remove(TEMP_USER_ACCOUNTS_FILE)

                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Verification code has expired. Please request a new one.')
        else:
            flash('Invalid verification code')

    return render_template('verify.html', username=username)
