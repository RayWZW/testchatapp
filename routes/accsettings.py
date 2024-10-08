from flask import Blueprint, render_template, redirect, url_for, session

accsettings_bp = Blueprint('accsettings', __name__)

@accsettings_bp.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if 'username' not in session:
        return redirect(url_for('login'))  

    username = session['username']  
    return render_template('account_settings.html', username=username)  