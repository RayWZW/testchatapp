from flask import Blueprint, request, jsonify, render_template, send_file, make_response
from utils.utils import load_json_file
import os

commands_bp = Blueprint('commands', __name__)

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'
HARDCODED_ADMIN_PASSWORD = '555ttt555$$'  # Hardcoded admin password

@commands_bp.route('/commands', methods=['GET'])
def commands():
    return render_template('commands.html')

@commands_bp.route('/commands', methods=['POST'])
def handle_command():
    data = request.json
    message = data.get('message')

    if message.startswith('!'):
        command_parts = message.split(' ')
        command = command_parts[0]
        
        if command == '!usercount':
            user_count = get_user_count()
            return jsonify({'response': f'CONSOLE: Current user count: {user_count}'})
        
        elif command == '!reload':
            return jsonify({'response': 'CONSOLE: Page will reload.'})
        
        elif command == '!downloaduserinfo':
            if len(command_parts) == 2:
                admin_password = command_parts[1]
                if check_admin_password(admin_password):
                    return prepare_user_accounts_file()
                else:
                    return jsonify({'response': 'CONSOLE: Invalid admin password.'})
            else:
                return jsonify({'response': 'CONSOLE: Password required for !downloaduserinfo command.'})
        
        elif command == '!clearchat':
            if len(command_parts) == 2:
                admin_password = command_parts[1]
                if check_admin_password(admin_password):
                    return clear_chat_logs()
                else:
                    return jsonify({'response': 'CONSOLE: Invalid admin password.'})
            else:
                return jsonify({'response': 'CONSOLE: Password required for !clearchat command.'})

        elif command == '!help':
            help_text = get_help_text()
            return jsonify({'response': f'CONSOLE: {help_text}'})
    
    return jsonify({'response': 'CONSOLE: Command not recognized'})

def prepare_user_accounts_file():
    if os.path.exists(USER_ACCOUNTS_FILE):
        with open(USER_ACCOUNTS_FILE, 'r') as file:
            data = file.read()
        response = make_response(data)
        response.headers['Content-Disposition'] = 'attachment; filename=useraccounts.json'
        response.mimetype = 'application/json'
        return response
    return jsonify({'response': 'CONSOLE: User accounts file not found.'})

def clear_chat_logs():
    if os.path.exists(CHAT_LOGS_FILE):
        os.remove(CHAT_LOGS_FILE)
        return jsonify({'response': 'CONSOLE: Chat logs cleared. The page will reload.'})
    return jsonify({'response': 'CONSOLE: Chat logs file not found.'})

def get_user_count():
    users = load_json_file(USER_ACCOUNTS_FILE)
    return len(users)

def get_help_text():
    return """
    Available commands:
    !usercount - Displays the current user count
    !reload - Reloads the page
    !downloaduserinfo <password> - Downloads the user accounts file (admin password required)
    !clearchat <password> - Clears the chat logs (admin password required)
    """

def check_admin_password(password):
    return password == HARDCODED_ADMIN_PASSWORD
