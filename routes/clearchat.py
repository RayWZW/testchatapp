from flask import Blueprint, jsonify
import os
from app import CHAT_LOGS_FILE  # Import CHAT_LOGS_FILE from your app module

clearchat_bp = Blueprint('clearchat', __name__)

@clearchat_bp.route('/clear-chatlogs', methods=['POST'])
def clear_chatlogs():
    try:
        if os.path.exists(CHAT_LOGS_FILE):
            os.remove(CHAT_LOGS_FILE)  # Delete the file
            return jsonify({"message": "Chatlogs deleted successfully"}), 200
        else:
            return jsonify({"error": "Chatlogs file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
