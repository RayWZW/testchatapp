from flask import Blueprint, jsonify

useraccounts_bp = Blueprint('useraccounts', __name__)

@useraccounts_bp.route('/data/user_accounts', methods=['POST'])
def handle_user_accounts():
    return jsonify({'message': 'Request successful'})
