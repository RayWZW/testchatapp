import json
import os
import random
import string
from PIL import Image
from functools import wraps
from flask import session, flash, redirect, url_for

# Load file paths from paths.json
with open('constants/paths.json') as f:
    paths = json.load(f)

USER_ACCOUNTS_FILE = paths["USER_ACCOUNTS_FILE"]
ADMINS_FILE = paths["ADMINS_FILE"]
ADMIN_PASSWORD_FILE = paths["ADMIN_PASSWORD_FILE"]

def load_json_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return {}

def save_json_file(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

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

def is_admin(username):
    admins = load_json_file(ADMINS_FILE)
    return username in admins

def get_admin_password():
    data = load_json_file(ADMIN_PASSWORD_FILE)
    return data.get('password', '')

def resize_image(input_path, output_path):
    with Image.open(input_path) as img:
        img = img.resize((50, 50), Image.ANTIALIAS)  # Resize to 50x50
        img.save(output_path)

def generate_unique_user_id(users):
    while True:
        unique_id = f"{random.randint(0, 9999999999):010d}"
        if unique_id not in users:
            return unique_id

# Add any other utility functions needed for your application below
