import time
import json
import os
import datetime
from flask_socketio import SocketIO

CHAT_LOGS_FILE = "data/chatlogs.json"
CONTENT_FILE_PATH = "utils/content.txt"  # Make sure to define this path

class ChatLogWatcher:
    def __init__(self, socketio):
        self.socketio = socketio
        self.last_chat_logs = None

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
                        if isinstance(message, dict) and message.get("username") == "George" and message.get("message") == ".clear":
                            self.clear_all_chats()
                            break

            except FileNotFoundError:
                time.sleep(0.09)
                continue
            except json.JSONDecodeError:
                time.sleep(0.09)
                continue
            except Exception:
                time.sleep(0.09)

            time.sleep(0.09)

def start_chatlog_watcher(socketio):
    watcher = ChatLogWatcher(socketio)
    watcher.check_for_updates()
