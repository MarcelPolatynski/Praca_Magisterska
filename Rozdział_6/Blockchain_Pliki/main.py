import hashlib
import json
from time import time
from flask import Flask, jsonify, request, send_from_directory
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_files = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'files': self.current_files,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_files = []
        self.chain.append(block)
        return block

    def new_file(self, file_data, file_name, file_size):
        self.current_files.append({
            'file_data': file_data,
            'file_name': file_name,
            'file_size': file_size,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
blockchain = Blockchain()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'mkv'}

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        with open(file_path, 'rb') as f:
            file_data = f.read()
        file_size = os.path.getsize(file_path)
        index = blockchain.new_file(file_data.hex(), filename, file_size)
        response = {
            'message': f'File will be added to Block {index}',
            'file_name': filename,
            'file_size': file_size,
            'block_index': index,
        }
        mine()
        return jsonify(response), 201
    return 'Invalid file type', 400

@app.route('/files', methods=['GET'])
def list_files():
    files = []
    for block in blockchain.chain:
        for file in block['files']:
            file_info = {
                'file_name': file['file_name'],
                'file_size': file['file_size'],
                'block_index': block['index'],
            }
            files.append(file_info)
    return jsonify(files), 200

@app.route('/files/<int:block_index>/<file_name>', methods=['GET'])
def get_file(block_index, file_name):
    for block in blockchain.chain:
        if block['index'] == block_index:
            for file in block['files']:
                if file['file_name'] == file_name:
                    file_data = bytes.fromhex(file['file_data'])
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    return send_from_directory(app.config['UPLOAD_FOLDER'], file_name), 200
    return 'File not found', 404

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message': 'New Block added',
        'index': block['index'],
        'files': block['files'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        'block_indexes': [block['index'] for block in blockchain.chain]
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
