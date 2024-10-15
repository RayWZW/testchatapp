from flask import Blueprint, render_template, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect

accsettings_bp = Blueprint('accsettings', __name__)
csrf = CSRFProtect()  # Initialize CSRF protection

@accsettings_bp.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    # No need to generate csrf_token here
    return render_template('account_settings.html', username=username)
