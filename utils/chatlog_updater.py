import time
import json
import os
import datetime
from flask_socketio import SocketIO

CHAT_LOGS_FILE = "data/chatlogs.json"
CONTENT_FILE_PATH = "utils/content.txt"
USER_ROLES_FILE = "data/userroles.json"

class ChatLogWatcher:
    def __init__(self, socketio):
        self.socketio = socketio
        self.last_chat_logs = None
        self.user_roles = self.load_user_roles()
        self.last_roles_update_time = os.path.getmtime(USER_ROLES_FILE) if os.path.exists(USER_ROLES_FILE) else 0

    def load_user_roles(self):
        if os.path.exists(USER_ROLES_FILE):
            with open(USER_ROLES_FILE, 'r') as f:
                return json.load(f)
        return {}

    def update_user_roles(self):
        current_mtime = os.path.getmtime(USER_ROLES_FILE)
        if current_mtime != self.last_roles_update_time:
            self.last_roles_update_time = current_mtime
            self.user_roles = self.load_user_roles()
            self.socketio.emit('user_roles_update', self.user_roles, namespace='/')

    def clear_all_chats(self):
        if os.path.exists(CONTENT_FILE_PATH):
            with open(CONTENT_FILE_PATH, 'r') as f:
                content = json.load(f)

            content['messages'][0]['timestamp'] = datetime.datetime.now().isoformat()

            with open(CHAT_LOGS_FILE, 'w') as f:
                json.dump(content, f)

            self.socketio.emit('chat_logs_update', {"messages": []}, namespace='/')

    def check_for_updates(self):
        while True:
            try:
                self.update_user_roles()

                if not os.path.exists(CHAT_LOGS_FILE):
                    time.sleep(0.09)
                    continue
                
                with open(CHAT_LOGS_FILE, 'r') as f:
                    content = f.read()
                    current_chat_logs = json.loads(content)

                if self.last_chat_logs != current_chat_logs:
                    self.socketio.emit('chat_logs_update', current_chat_logs, namespace='/')
                    self.last_chat_logs = current_chat_logs

                    for message in current_chat_logs.get("messages", []):
                        username = message.get("username")
                        user_message = message.get("message")


            except FileNotFoundError:
                time.sleep(0.09)
                continue
            except json.JSONDecodeError:
                time.sleep(0.09)
                continue
            except Exception as e:
                print(f"Error in chat log watcher: {e}")
                time.sleep(0.09)

            time.sleep(0.09)

def start_chatlog_watcher(socketio):
    watcher = ChatLogWatcher(socketio)
    watcher.check_for_updates()
