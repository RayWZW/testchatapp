from flask import Blueprint, request, jsonify, send_from_directory, url_for
from PIL import Image
from moviepy.editor import VideoFileClip
import os
import mimetypes
import time
import logging
import hashlib

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = 'uploads'

# Configure logging
logging.basicConfig(level=logging.INFO)

def generate_file_hash(file):
    file.seek(0)
    hasher = hashlib.md5()
    hasher.update(file.read())
    file.seek(0)  # Reset the file pointer after reading
    return hasher.hexdigest()

@files_bp.route('/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    original_filename = file.filename.lower()
    timestamp = int(time.time())
    file_hash = generate_file_hash(file)
    
    # Generate a new filename using the hash
    new_filename = f"{file_hash}_{timestamp}{os.path.splitext(original_filename)[1]}"
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)

    image_mime_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    video_mime_types = ['video/mp4', 'video/x-msvideo', 'video/x-flv']
    mime_type = mimetypes.guess_type(original_filename)[0]

    try:
        # Check if a processed version already exists
        if os.path.exists(file_path):
            logging.info(f"File already processed: {file_path}")
            return jsonify({'file_url': url_for('files.download_file', filename=new_filename), 'file_type': mimetypes.guess_type(file_path)[0]})

        if mime_type in image_mime_types:
            with Image.open(file) as img:
                img = img.resize((500, 500))
                img.save(file_path)
        elif mime_type in video_mime_types:
            temp_video_path = os.path.join(UPLOAD_FOLDER, 'temp_' + new_filename)
            file.save(temp_video_path)

            try:
                with VideoFileClip(temp_video_path) as video:
                    video_resized = video.resize(height=500)
                    video_resized.write_videofile(file_path, codec='libx264', audio_codec='aac')
            except Exception as e:
                logging.error(f"Error processing video '{original_filename}': {str(e)}")
                return jsonify({'error': 'Video processing failed. Please check the format.'}), 400
            finally:
                if os.path.exists(temp_video_path):
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
