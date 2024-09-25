# utils/files.py
from flask import Blueprint, request, jsonify, send_from_directory, url_for, current_app
from PIL import Image
import os
import mimetypes
import time

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = 'uploads'

@files_bp.route('/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    original_filename = file.filename.lower()
    timestamp = int(time.time())
    filename, file_extension = os.path.splitext(original_filename)
    new_filename = f"{filename}_{timestamp}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)

    image_mime_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    video_mime_types = ['video/mp4', 'video/x-msvideo', 'video/x-flv']
    mime_type = mimetypes.guess_type(original_filename)[0]

    try:
        if mime_type in image_mime_types:
            with Image.open(file) as img:
                img = img.resize((500, 500))
                img.save(file_path)
        elif mime_type in video_mime_types:
            file.save(file_path)
        else:
            file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

    file_url = url_for('files.download_file', filename=new_filename)
    file_type = mimetypes.guess_type(file_path)[0]
    return jsonify({'file_url': file_url, 'file_type': file_type})

@files_bp.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
