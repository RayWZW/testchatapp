from flask import Blueprint, request, jsonify
from utils.utils import load_json_file

userinfo_bp = Blueprint('userinfo', __name__)

USER_ACCOUNTS_FILE = 'data/useraccounts.json'  

@userinfo_bp.route('/get_user_info', methods=['GET'])
def get_user_info():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'No username provided'}), 400

    users = load_json_file(USER_ACCOUNTS_FILE)
    if username not in users:
        return jsonify({'error': 'User not found'}), 404

    user_info = {
        'username': username,
        'email': users[username].get('email', 'N/A'),
        'registered_at': users[username].get('registered_at', 'N/A')
    }
    return jsonify(user_info)
