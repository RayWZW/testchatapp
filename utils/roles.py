import json
import os
from flask import Blueprint, request, jsonify

roles_bp = Blueprint('roles', __name__)

USER_ROLES_FILE = 'data/userroles.json'  # Change to new roles file

# Load the user roles from the specified JSON file
def load_user_roles(file_path):
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r') as f:
        return json.load(f)

# Save the updated user roles back to the JSON file
def save_user_roles(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Add a role to a user
def add_role(username, role):
    users = load_user_roles(USER_ROLES_FILE)  # Load user roles
    if username not in users:
        users[username] = {'additionalRoles': []}  # Initialize if user does not exist

    if role in users[username]['additionalRoles']:
        return {'success': False, 'message': 'Role already exists.'}

    users[username]['additionalRoles'].append(role)
    save_user_roles(USER_ROLES_FILE, users)  # Save the updated user roles
    return {'success': True, 'message': f'Role {role} added to user {username}.'}

# Remove a role from a user
def remove_role(username, role):
    users = load_user_roles(USER_ROLES_FILE)  # Load user roles
    if username not in users:
        return {'success': False, 'message': 'User not found.'}
    
    if role not in users[username].get('additionalRoles', []):
        return {'success': False, 'message': 'Role does not exist.'}

    users[username]['additionalRoles'].remove(role)
    save_user_roles(USER_ROLES_FILE, users)  # Save the updated user roles
    return {'success': True, 'message': f'Role {role} removed from user {username}.'}

# Get additional roles for a specific user
def get_user_roles(username):
    users = load_user_roles(USER_ROLES_FILE)  # Load user roles
    if username not in users:
        return []

    return users[username].get('additionalRoles', [])

# Define the endpoints

@roles_bp.route('/add_role', methods=['POST'])
def add_role_endpoint():
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    
    if not username or not role:
        return jsonify({'success': False, 'message': 'Username and role are required.'}), 400
    
    result = add_role(username, role)
    return jsonify(result)

@roles_bp.route('/remove_role', methods=['POST'])
def remove_role_endpoint():
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    
    if not username or not role:
        return jsonify({'success': False, 'message': 'Username and role are required.'}), 400
    
    result = remove_role(username, role)
    return jsonify(result)

@roles_bp.route('/data/userroles.json', methods=['GET', 'POST'])
def serve_user_roles():
    if request.method == 'GET':
        if os.path.exists(USER_ROLES_FILE):
            with open(USER_ROLES_FILE, 'r') as f:
                data = f.read()
            return data, 200, {'Content-Type': 'application/json'}
        else:
            return jsonify({'error': 'File not found.'}), 404

    if request.method == 'POST':
        new_data = request.get_json()
        with open(USER_ROLES_FILE, 'w') as f:
            json.dump(new_data, f, indent=4)
        return jsonify({'success': True, 'message': 'Roles updated successfully.'}), 200



# Register the blueprint in your main application file (e.g., app.py)
