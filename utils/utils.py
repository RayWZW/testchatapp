# utils.py

import json
import os
import random
import string

def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

import random

def generate_unique_user_id(users):
    while True:
        unique_id = f"{random.randint(0, 9999999999):010d}"
        if unique_id not in (user['user_id'] for user in users.values()):
            return unique_id
        


def generate_dm_token(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))        
