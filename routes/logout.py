from flask import Blueprint, session, redirect, url_for

logout_bp = Blueprint('logout', __name__)

active_sessions = {}  

@logout_bp.route('/logout')
def logout():
    username = session.get('username')
    if username in active_sessions:
        del active_sessions[username]
    session.pop('username', None)
    return redirect(url_for('login.login'))  
