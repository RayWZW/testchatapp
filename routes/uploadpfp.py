from flask import Blueprint, request, jsonify, session, url_for, current_app
import os

upload_pfp_bp = Blueprint('upload_pfp', __name__)

@upload_pfp_bp.route('/upload_pfp', methods=['POST'])
def upload_pfp():
    if 'pfp' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pfp']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    username = session.get('username')  
    if username is None:
        return jsonify({'error': 'User not logged in'}), 401

    pfp_folder = current_app.config['PFP_FOLDER']
    file_path = os.path.join(pfp_folder, f"{username.lower()}.png")

    os.makedirs(pfp_folder, exist_ok=True)

    file.save(file_path)

    return jsonify({
        'message': 'Profile picture updated successfully!',
        'url': url_for('static', filename=f'pfps/{username.lower()}.png')
    })