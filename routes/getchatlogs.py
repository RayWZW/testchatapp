from flask import Blueprint, jsonify
import json
import os

getchatlogs_bp = Blueprint('getchatlogs', __name__)

@getchatlogs_bp.route('/data/chatlogs.json', methods=['GET'])
def get_chatlogs():
    try:
        # Make sure to use the correct path to your chatlogs file
        chatlogs_file_path = 'data/chatlogs.json'
        with open(chatlogs_file_path, 'r') as f:
            chatlogs = json.load(f)
        return jsonify(chatlogs), 200
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400
