from flask import Blueprint, request, jsonify, render_template, make_response
from utils.utils import load_json_file
import os
import json
import random
import requests
import datetime

commands_bp = Blueprint('commands', __name__)

USER_ACCOUNTS_FILE = 'data/useraccounts.json'
CHAT_LOGS_FILE = 'data/chatlogs.json'
MESSAGE_LOG_FILE = 'data/message_log.json'
HARDCODED_ADMIN_PASSWORD = 'Georgedollasign$$'
CONTENT_FILE_PATH = 'utils/content.txt'

@commands_bp.route('/commands', methods=['GET'])
def commands():
    messages = load_messages()
    return render_template('commands.html', messages=messages)

@commands_bp.route('/jumpscare', methods=['GET'])
def jumpscare():
    return render_template('jumpscare.html')


@commands_bp.route('/commands', methods=['POST'])
def handle_command():
    data = request.json
    message = data.get('message')

    if message.startswith('!'):
        log_message(message)

        command_parts = message.split(' ')
        command = command_parts[0]

        if command == '!autocomplete':
            return jsonify({'response': suggest_commands(command_parts[1] if len(command_parts) > 1 else '')})

        if command == '!usercount':
            user_count = get_user_count()
            return jsonify({'response': f'CONSOLE: Current user count: {user_count}'})

        if command == '!reload':
            return jsonify({'response': 'CONSOLE: Page will reload.', 'reload': True})

        if command == '!downloaduserinfo':
            if len(command_parts) == 2:
                admin_password = command_parts[1]
                if admin_password == HARDCODED_ADMIN_PASSWORD:
                    return prepare_user_accounts_file()
                return jsonify({'response': 'CONSOLE: Invalid admin password.'})
            return jsonify({'response': 'CONSOLE: Password required for !downloaduserinfo command.'})

        if command == '!clearchat':
            if len(command_parts) == 2:
                admin_password = command_parts[1]
                if admin_password == HARDCODED_ADMIN_PASSWORD:
                    return clear_chat_logs()
                return jsonify({'response': 'CONSOLE: Invalid admin password.'})
            return jsonify({'response': 'CONSOLE: Password required for !clearchat command.'})

        if command == '!help':
            help_text = get_help_text()
            return jsonify({'response': f'CONSOLE: {help_text}'})

        if command == '!info':
            return jsonify({'response': 'CONSOLE: THUG CHAT, CREATED BY GEORGE, A COOL CHAT WEBSITE FOR USER INTERACTION.'})

        if command == '!restart':
            if len(command_parts) == 2:
                admin_password = command_parts[1]
                if admin_password == HARDCODED_ADMIN_PASSWORD:
                    restart_server()
                    return jsonify({'response': 'CONSOLE: Server is restarting...'})
                return jsonify({'response': 'CONSOLE: Invalid admin password for !restart command.'})
            return jsonify({'response': 'CONSOLE: Admin password required for !restart command.'})

        if command == '!listusers':
            users = list_users()
            return jsonify({'response': f'CONSOLE: Current users: {", ".join(users)}'})

        if command == '!getuserinfo':
            if len(command_parts) == 2:
                username = command_parts[1]
                user_info = get_user_info(username)
                return jsonify({'response': f'CONSOLE: User Info: {user_info}'})
            return jsonify({'response': 'CONSOLE: Please provide a username.'})

        if command == '!calculate':
            if len(command_parts) >= 2:
                expression = ' '.join(command_parts[1:])
                return calculate(expression)
            return jsonify({'response': 'CONSOLE: Usage: !calculate <expression>'})

        if command == '!dice':
            if len(command_parts) == 2:
                try:
                    sides = int(command_parts[1])
                    if sides > 0:
                        return jsonify({'response': f'CONSOLE: You rolled a {random.randint(1, sides)}!'})
                    return jsonify({'response': 'CONSOLE: Number of sides must be greater than 0.'})
                except ValueError:
                    return jsonify({'response': 'CONSOLE: Please provide a valid number of sides.'})

        if command == '!webreq':
            if len(command_parts) >= 3:
                webhook_url = command_parts[1].strip('"')
                message = ' '.join(command_parts[2:])
                return send_webhook_message(webhook_url, message)
            return jsonify({'response': 'CONSOLE: Usage: !webreq "<webhook_url>" "<message>"'})

    return jsonify({'response': 'CONSOLE: Command not recognized'})


def suggest_commands(prefix):
    available_commands = [
        '!usercount', '!reload', '!downloaduserinfo', '!clearchat', '!help',
        '!info', '!restart', '!listusers', '!getuserinfo', '!createuser',
        '!removeuser', '!calculate', '!dice', '!webreq', '!autocomplete'
    ]
    suggestions = [cmd for cmd in available_commands if cmd.startswith(prefix)]
    return suggestions

def load_messages():
    if os.path.exists(MESSAGE_LOG_FILE):
        with open(MESSAGE_LOG_FILE, 'r') as file:
            return json.load(file)
    return []

def log_message(message):
    messages = load_messages()
    messages.append(message)
    with open(MESSAGE_LOG_FILE, 'w') as file:
        json.dump(messages, file)

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

    # Read content from content.txt
    with open(CONTENT_FILE_PATH, 'r') as f:
        content = json.load(f)

    # Update the timestamp in the content
    content['messages'][0]['timestamp'] = datetime.datetime.now().isoformat()

    # Write the updated content back to the CHAT_LOGS_FILE without deleting it
    with open(CHAT_LOGS_FILE, 'w') as f:
        json.dump(content, f)

    return jsonify({'message': 'All chat logs updated successfully'})

def get_user_count():
    users = load_json_file(USER_ACCOUNTS_FILE)
    return len(users)

def list_users():
    users = load_json_file(USER_ACCOUNTS_FILE)
    return list(users.keys())

def get_user_info(username):
    users = load_json_file(USER_ACCOUNTS_FILE)
    user_info = users.get(username)
    if user_info:
        profile_pic_url = f"https://thugchat.ddns.net/static/pfps/{username}.png"
        profile_pic_link = f'<a href="{profile_pic_url}" target="_blank">Profile Picture</a>'
        return (f"Username: {username}, Registered at: {user_info.get('registered_at')}, "
                f"{profile_pic_link}")
    return 'User not found.'


from sympy import symbols, Eq, solve, sympify, N 

def calculate(expression):
    # Define the variable(s) you want to solve for
    x = symbols('x')

    try:
        # Check if the expression contains an equality sign
        if '=' in expression:
            # Split the equation into left and right parts
            left, right = expression.split('=')
            equation = Eq(sympify(left.strip()), sympify(right.strip()))
            solution = solve(equation, x)  # Solve for x
            return jsonify({'response': f'CONSOLE: Solution: x = {solution}'})
        else:
            # Regular calculation
            result = N(sympify(expression))
            return jsonify({'response': f'CONSOLE: Result: {result}'})
    except Exception as e:
        return jsonify({'response': f'CONSOLE: Error in calculation: {str(e)}'})


def send_webhook_message(webhook_url, message):
    try:
        response = requests.post(webhook_url, json={"content": message})
        if response.status_code == 204:
            return jsonify({'response': 'CONSOLE: Message sent successfully.'})
        return jsonify({'response': f'CONSOLE: Failed to send message. Status code: {response.status_code}'})
    except Exception as e:
        return jsonify({'response': f'CONSOLE: Error sending webhook message: {str(e)}'})

def get_help_text():
    return """
    Available commands:
    !usercount - Displays the current user count
    !reload - Reloads the page
    !downloaduserinfo <password> - Downloads the user accounts file (admin password required)
    !clearchat <password> - Clears the chat logs (admin password required)
    !info - Provides information about the chat application
    !restart <password> - Restarts the server (admin password required)
    !listusers - Lists the current users
    !getuserinfo <username> - Gets information about a specific user
    !calculate <expression> - Evaluates a mathematical expression (supports +, -, *, /)
    !dice <sides> - Rolls a dice with a specified number of sides
    !webreq "<webhook_url>" "<message>" - Sends a message to the specified webhook
    !autocomplete <partial_command> - Suggests available commands based on input
    """

