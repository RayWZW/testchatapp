from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_wtf.csrf import CSRFProtect, generate_csrf
import os
import random
import smtplib
from datetime import datetime, timedelta
from utils.utils import load_json_file, save_json_file

password_reset_bp = Blueprint('password_reset', __name__)
csrf = CSRFProtect()

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
TEMP_USER_ACCOUNTS_FILE = 'data/temp_useraccounts.json'

def send_reset_email(email, code):
    smtp_server = "smtp.fastmail.com"
    port = 587
    username = "thugverify11@fastmail.com"
    password = "28642x4c2p8q5d74"  # Your app-specific password
    subject = "Password Reset Request"
    body = f"Your password reset code is: {code}"

    message = f'From: {username}\nTo: {email}\nSubject: {subject}\n\n{body}'

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, email, message)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

@password_reset_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        users = load_json_file(USER_ACCOUNTS_FILE)

        user = users.get(username)

        if user:
            temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE) if os.path.exists(TEMP_USER_ACCOUNTS_FILE) else {}
            current_time = datetime.now()

            if username in temporary_users:
                reset_time = datetime.strptime(temporary_users[username]['reset_time'], '%Y-%m-%d %H:%M:%S')
                if current_time < reset_time + timedelta(minutes=5):
                    flash('You can only request a new reset code every 5 minutes.')
                    return render_template('forgot_password.html', csrf_token=generate_csrf())

            reset_code = random.randint(100000, 999999)
            send_reset_email(user['email'], reset_code)

            temporary_users[username] = {
                'reset_code': reset_code,
                'reset_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            save_json_file(TEMP_USER_ACCOUNTS_FILE, temporary_users)

            flash('A password reset code has been sent to your email.')
            return redirect(url_for('password_reset.enter_code', username=username))  # Redirect to enter code page

        flash('User not found.')
        return render_template('forgot_password.html', csrf_token=generate_csrf())

    return render_template('forgot_password.html', csrf_token=generate_csrf())

@password_reset_bp.route('/enter-code/<username>', methods=['GET', 'POST'])
def enter_code(username):
    if request.method == 'POST':
        code_entered = request.form['code']
        temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE)
        user = temporary_users.get(username)

        if user:
            reset_time = datetime.strptime(user['reset_time'], '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()

            if str(user['reset_code']) == code_entered:
                if (current_time - reset_time).total_seconds() <= 600:  # Code is valid for 10 minutes
                    return redirect(url_for('password_reset.reset_password', username=username))  # Redirect to set new password
                else:
                    flash('Reset code has expired. Please request a new one.')
            else:
                flash('Invalid reset code.')

    return render_template('enter_code.html', username=username, csrf_token=generate_csrf())  # Render the code entry template

@password_reset_bp.route('/reset-password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    if request.method == 'POST':
        new_password = request.form['new_password']
        temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE)
        if username in temporary_users:
            users = load_json_file(USER_ACCOUNTS_FILE)
            users[username]['password'] = new_password  # Ensure to hash the password here

            save_json_file(USER_ACCOUNTS_FILE, users)
            del temporary_users[username]  # Remove temporary user data
            save_json_file(TEMP_USER_ACCOUNTS_FILE, temporary_users)

            flash('Your password has been reset successfully!')
            return redirect(url_for('login.login'))  # Redirect to login.login page

    return render_template('reset_password.html', username=username, csrf_token=generate_csrf())  # Render the reset password template
