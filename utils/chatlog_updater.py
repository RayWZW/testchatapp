import time
import json
import os
from flask_socketio import SocketIO

CHAT_LOGS_FILE = "data/chatlogs.json"

class ChatLogWatcher:
    def __init__(self, socketio):
        self.socketio = socketio
        self.last_chat_logs = None

    def check_for_updates(self):
        while True:
            try:
                with open(CHAT_LOGS_FILE, 'r') as f:
                    current_chat_logs = json.load(f)

                # Check if the current chat logs have changed
                if self.last_chat_logs != current_chat_logs:
                    print("Chat logs have changed, emitting update...")
                    self.socketio.emit('chat_logs_update', current_chat_logs, namespace='/')
                    self.last_chat_logs = current_chat_logs  # Update the last seen chat logs
            

            except Exception as e:
                print(f"Error reading chat logs: {e}")

            time.sleep(0.09)  # Wait for 50 ms

def start_chatlog_watcher(socketio):
    watcher = ChatLogWatcher(socketio)
    watcher.check_for_updates()
