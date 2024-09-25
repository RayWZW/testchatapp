from flask import Blueprint, flash, redirect, url_for, render_template, request
import os
import random
import smtplib
from datetime import datetime, timedelta
from utils.utils import load_json_file, save_json_file

password_reset_bp = Blueprint('password_reset', __name__)

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

        # Check if the email exists in user accounts
        user = users.get(username)

        if user:
            temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE) if os.path.exists(TEMP_USER_ACCOUNTS_FILE) else {}
            current_time = datetime.now()

            # Check if the user already requested a reset code recently
            if username in temporary_users:
                reset_time = datetime.strptime(temporary_users[username]['reset_time'], '%Y-%m-%d %H:%M:%S')
                if current_time < reset_time + timedelta(minutes=5):
                    flash('You can only request a new reset code every 5 minutes.')
                    return render_template('forgot_password.html')

            reset_code = random.randint(100000, 999999)
            send_reset_email(user['email'], reset_code)

            # Save the reset code and timestamp to the temporary file
            temporary_users[username] = {
                'reset_code': reset_code,
                'reset_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            save_json_file(TEMP_USER_ACCOUNTS_FILE, temporary_users)

            flash('A password reset code has been sent to your email.')
            return redirect(url_for('password_reset.forgot_password'))

        flash('User not found.')
        return render_template('forgot_password.html')

    return render_template('forgot_password.html')

@password_reset_bp.route('/reset-password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE)
    user = temporary_users.get(username)

    if request.method == 'POST':
        code_entered = request.form['code']
        new_password = request.form['new_password']
        current_time = datetime.now()
        reset_time = datetime.strptime(user['reset_time'], '%Y-%m-%d %H:%M:%S')

        if user and str(user['reset_code']) == code_entered:
            if (current_time - reset_time).total_seconds() <= 600:  # Code is valid for 10 minutes
                users = load_json_file(USER_ACCOUNTS_FILE)
                users[username]['password'] = new_password  # Hash the password here

                save_json_file(USER_ACCOUNTS_FILE, users)
                
                del temporary_users[username]  # Remove the temporary user data
                save_json_file(TEMP_USER_ACCOUNTS_FILE, temporary_users)

                flash('Your password has been reset successfully!')
                return redirect(url_for('login'))  # Redirect to the login page

            flash('Reset code has expired. Please request a new one.')
        else:
            flash('Invalid reset code.')

    return render_template('reset_password.html', username=username)
