from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from data_store import USERS, FILES
from helper_functions import generate_token, check_file_type

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data['email']
    password = data['password']

    if email in USERS:
        return jsonify({'message': 'User already exists'}), 400

    USERS[email] = {
        'password': password,
        'verified': False,
        'type': 'client'
    }

    token = generate_token(email)
    return jsonify({'message': 'Signup successful', 'verification_link': f'/verify/{token}'})

@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    email = token[::-1]  # Just reversed string for simplicity
    if email in USERS:
        USERS[email]['verified'] = True
        return jsonify({'message': 'Email verified'})
    return jsonify({'message': 'Invalid token'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    user = USERS.get(email)
    if user and user['password'] == password:
        return jsonify({'message': 'Login successful', 'user_type': user["type"]})
    return jsonify({'message': 'Invalid login'}), 401

@app.route('/upload', methods=['POST'])
def upload():
    user_type = request.form.get('user_type')
    if user_type != 'ops':
        return jsonify({'message': 'Only ops user can upload'}), 403

    file = request.files.get('file')
    if file and check_file_type(file.filename):
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, file_id + "_" + filename)
        file.save(path)

        FILES[file_id] = {'filename': filename, 'path': path}
        return jsonify({'message': 'File uploaded', 'file_id': file_id})
    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/download/<file_id>', methods=['GET'])
def download(file_id):
    user_type = request.args.get('user_type')
    if user_type != 'client':
        return jsonify({'message': 'Only client users can download'}), 403

    if file_id not in FILES:
        return jsonify({'message': 'File not found'}), 404

    token = generate_token(file_id)
    return jsonify({'download_link': f'/getfile/{token}', 'message': 'success'})

@app.route('/getfile/<token>', methods=['GET'])
def getfile(token):
    file_id = token[::-1]  # Reverse back
    if file_id in FILES:
        file = FILES[file_id]
        return jsonify({'filename': file['filename'], 'path': file['path']})
    return jsonify({'message': 'Invalid or expired link'}), 404

@app.route('/files', methods=['GET'])
def list_files():
    return jsonify({'files': [f['filename'] for f in FILES.values()]})

if __name__ == '__main__':
    app.run(debug=True)
