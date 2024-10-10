import json
import os

class UserBioManager:
    def __init__(self, filepath='data/bios.json'):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.isfile(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)

    def add_bio(self, username, bio):
        with open(self.filepath, 'r+') as f:
            data = json.load(f)
            data[username] = {
                'username': username,
                'bio': bio
            }
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def get_bio(self, username):
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            return data.get(username, {}).get('bio', '')

    def update_bio(self, username, new_bio):
        with open(self.filepath, 'r+') as f:
            data = json.load(f)
            if username in data:
                data[username]['bio'] = new_bio
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

    def delete_bio(self, username):
        with open(self.filepath, 'r+') as f:
            data = json.load(f)
            if username in data:
                del data[username]
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
