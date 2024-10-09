from flask import Blueprint, session, jsonify, request
from utils.utils import load_json_file, save_json_file
from app import USER_ACCOUNTS_FILE, BANNED_USERS_FILE  

ban_bp = Blueprint('ban', __name__)
active_sessions = {}  

def is_admin(username):
    admins = load_json_file('data/admins.json')
    return username in admins

@ban_bp.route('/ban_user', methods=['POST'])
def ban_user():
    if 'username' not in session or not is_admin(session['username']):
        return jsonify({'message': 'Unauthorized'}), 403

    username = request.json.get('username')
    if not username:
        return jsonify({'message': 'No username provided'}), 400

    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return jsonify({'message': 'User not found'}), 404

    user_details = users[username]

    banned_users = load_json_file(BANNED_USERS_FILE)
    banned_users[username] = {
        'password': user_details['password'],
        'email': user_details['email'],
        'registered_at': user_details['registered_at'],
        'public_ip': user_details.get('public_ip', '')
    }
    save_json_file(BANNED_USERS_FILE, banned_users)

    del users[username]
    save_json_file(USER_ACCOUNTS_FILE, users)

    if username in active_sessions:
        for session_id in active_sessions[username]:
            socketio.disconnect(sid=session_id)

    if username in session:
        session.pop(username, None)
        return jsonify({
            'message': 'User banned and deleted successfully',
            'redirect': '/logout'
        })

    return jsonify({
        'message': 'User banned and deleted successfully',
        'redirect': None
    })