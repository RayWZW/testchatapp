from flask import Blueprint, request, jsonify, send_from_directory, url_for
from PIL import Image
from moviepy.editor import VideoFileClip
import os
import mimetypes
import time
import logging

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = 'uploads'

# Configure logging
logging.basicConfig(level=logging.INFO)

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
            # Save the uploaded video file to a temporary location
            temp_video_path = os.path.join(UPLOAD_FOLDER, 'temp_' + new_filename)
            file.save(temp_video_path)

            # Process the video using the temporary path
            with VideoFileClip(temp_video_path) as video:
                video_resized = video.resize(height=500)
                video_resized.write_videofile(file_path, codec='libx264', audio_codec='aac')
            
            # Remove the temporary file after processing
            os.remove(temp_video_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

    except Exception as e:
        logging.error(f"Error processing file '{original_filename}': {str(e)}")
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

    file_url = url_for('files.download_file', filename=new_filename)
    file_type = mimetypes.guess_type(file_path)[0]
    return jsonify({'file_url': file_url, 'file_type': file_type})

@files_bp.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
