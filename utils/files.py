from flask import Blueprint, request, jsonify, send_from_directory, url_for
from PIL import Image
import os
import mimetypes
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
    file_hash = generate_file_hash(file)

    # Generate a filename using the hash
    existing_filename = f"{file_hash}{os.path.splitext(original_filename)[1]}"
    existing_file_path = os.path.join(UPLOAD_FOLDER, existing_filename)

    image_mime_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    mime_type = mimetypes.guess_type(original_filename)[0]

    # Check if the file already exists, if so, return the existing file URL without creating a new one
    if os.path.exists(existing_file_path):
        logging.info(f"File already exists: {existing_file_path}")
        file_url = url_for('files.download_file', filename=existing_filename)
        file_type = mimetypes.guess_type(existing_file_path)[0]
        return jsonify({'file_url': file_url, 'file_type': file_type})

    # Process the file if it's an image and save it
    try:
        # Handle image files
        if mime_type in image_mime_types:
            # Skip processing if the file is a GIF
            if mime_type == 'image/gif':
                file.save(existing_file_path)  # Save GIF directly without resizing
            else:
                with Image.open(file) as img:
                    img = img.resize((500, 500))  # Resize non-GIF images
                    img.save(existing_file_path)

        # Save non-media files directly
        else:
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
