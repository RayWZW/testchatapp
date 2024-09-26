from flask import Blueprint, request, jsonify, send_from_directory, url_for
from PIL import Image
from moviepy.editor import VideoFileClip
import os
import mimetypes
import time
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = 'uploads'

# Configure logging
logging.basicConfig(level=logging.INFO)

# ThreadPoolExecutor for handling video processing in the background
executor = ThreadPoolExecutor(max_workers=4)

def generate_file_hash(file):
    file.seek(0)
    hasher = hashlib.md5()
    hasher.update(file.read())
    file.seek(0)  # Reset the file pointer after reading
    return hasher.hexdigest()

def process_video(temp_video_path, output_video_path):
    """Function to process and resize video in a background thread."""
    try:
        with VideoFileClip(temp_video_path) as video:
            video_resized = video.resize(height=500)
            video_resized.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
    except Exception as e:
        logging.error(f"Error processing video '{temp_video_path}': {str(e)}")
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

@files_bp.route('/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    original_filename = file.filename.lower()
    file_hash = generate_file_hash(file)

    # Generate a filename using the hash, no timestamp is needed
    existing_filename = f"{file_hash}{os.path.splitext(original_filename)[1]}"
    existing_file_path = os.path.join(UPLOAD_FOLDER, existing_filename)

    image_mime_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    video_mime_types = ['video/mp4', 'video/x-msvideo', 'video/x-flv', 'video/quicktime']
    mime_type = mimetypes.guess_type(original_filename)[0]

    # Check if the file already exists, if so, return the existing file URL without creating a new one
    if os.path.exists(existing_file_path):
        logging.info(f"File already exists: {existing_file_path}")
        file_url = url_for('files.download_file', filename=existing_filename)
        file_type = mimetypes.guess_type(existing_file_path)[0]
        return jsonify({'file_url': file_url, 'file_type': file_type})

    # Process the file if it's an image or video and save it
    try:
        if mime_type in image_mime_types:
            with Image.open(file) as img:
                img = img.resize((500, 500))
                img.save(existing_file_path)
        elif mime_type in video_mime_types:
            temp_video_path = os.path.join(UPLOAD_FOLDER, 'temp_' + existing_filename)
            file.save(temp_video_path)

            # Process video in a separate thread to avoid blocking the main thread
            executor.submit(process_video, temp_video_path, existing_file_path)

            # Return response immediately while the video is being processed
            return jsonify({'message': 'Video is being processed', 'file_url': url_for('files.download_file', filename=existing_filename)})

        else:
            # Save non-media files directly
            file.save(existing_file_path)

    except Exception as e:
        logging.error(f"Error processing file '{original_filename}': {str(e)}")
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

    # Return the URL of the newly uploaded file
    file_url = url_for('files.download_file', filename=existing_filename)
    file_type = mimetypes.guess_type(existing_file_path)[0]
    return jsonify({'file_url': file_url, 'file_type': file_type})

@files_bp.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
