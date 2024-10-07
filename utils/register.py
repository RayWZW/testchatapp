from flask import Blueprint, flash, redirect, url_for, session, render_template, request
from datetime import datetime
import os
import random
import smtplib
from werkzeug.utils import secure_filename
from PIL import Image
from utils.utils import load_json_file, save_json_file, generate_unique_user_id

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
TEMP_USER_ACCOUNTS_FILE = 'data/temp_useraccounts.json'
BANNED_USERS_FILE = 'data/banned.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

register_bp = Blueprint('register', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_verification_email(email, code):
    smtp_server = "smtp.fastmail.com"
    port = 587
    username = "thugverify11@fastmail.com"
    password = "28642x4c2p8q5d74"
    subject = "THUG-CHAT Verification"
    body = f"Your verification code is: {code}"
    message = f'From: {username}\nTo: {email}\nSubject: {subject}\n\n{body}'

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, email, message)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        public_ip = request.form['public_ip']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if len(username) < 6 or len(password) < 6:
            flash('Username and password must be at least 6 characters long')
            return render_template('register.html')

        users = load_json_file(USER_ACCOUNTS_FILE)
        banned_users = load_json_file(BANNED_USERS_FILE)

        # Check if the IP is in banned users
        if any(banned_user['public_ip'] == public_ip for banned_user in banned_users.values()):
            flash('Registration from this IP address is blocked due to a ban.')
            return render_template('register.html')

        if username in banned_users:
            flash('This user is banned and cannot register again')
            return render_template('register.html')

        if username in users:
            flash('Username already exists')
            return render_template('register.html')

        if any(user['email'] == email for user in users.values()):
            flash('An account with this email already exists')
            return render_template('register.html')

        # Check if the IP address is already registered
        if any(user['public_ip'] == public_ip for user in users.values()):
            flash('An account with this IP address already exists. One account per IP is allowed.')
            return render_template('register.html')

        profile_picture = request.files.get('pfp')
        if profile_picture and allowed_file(profile_picture.filename):
            os.makedirs('static/pfps', exist_ok=True)
            filename = secure_filename(f"{username}.png")
            file_path = os.path.join('static/pfps', filename)

            img = Image.open(profile_picture)
            img = img.resize((50, 50))  # Resize to 50x50
            img.save(file_path)
        else:
            flash('Invalid profile picture. Please upload a valid image file.')
            return render_template('register.html')

        verification_code = random.randint(100000, 999999)
        send_verification_email(email, verification_code)

        temporary_users = load_json_file(TEMP_USER_ACCOUNTS_FILE) if os.path.exists(TEMP_USER_ACCOUNTS_FILE) else {}
        temporary_users[username] = {
            'password': password,
            'email': email,
            'public_ip': public_ip,
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
                    'public_ip': user['public_ip'],
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
