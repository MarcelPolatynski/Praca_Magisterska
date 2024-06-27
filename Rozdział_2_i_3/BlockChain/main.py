import hashlib
import json
from time import time
from flask import Flask, jsonify, request, send_from_directory
import os

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_tasks = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'tasks': self.current_tasks,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_tasks = []
        self.chain.append(block)
        return block

    def new_task(self, title, description):
        task_id = self.get_next_task_id()
        self.current_tasks.append({'id': task_id, 'title': title, 'description': description, 'completed': False, 'deleted': False})
        return self.last_block['index'] + 1

    def delete_task(self, task_id):
        block, task_index = self.find_task(task_id)
        if block is not None and task_index is not None:
            current_task = block['tasks'][task_index]
            self.new_task_transaction(task_id, current_task['title'], current_task['description'], current_task['completed'], True)
            return True
        return False

    def edit_task(self, task_id, title, description, completed):
        block, task_index = self.find_task(task_id)
        if block is not None and task_index is not None:
            current_task = block['tasks'][task_index]
            title = title if title is not None else current_task['title']
            description = description if description is not None else current_task['description']
            completed = completed if completed is not None else current_task['completed']
            self.new_task_transaction(task_id, title, description, completed, False)
            return True
        return False

    def new_task_transaction(self, task_id, title, description, completed, deleted):
        transaction = {
            'id': task_id,
            'title': title,
            'description': description,
            'completed': completed,
            'deleted': deleted
        }
        self.current_tasks.append(transaction)

    def update_task_status(self, task_id, completed):
        block, task_index = self.find_task(task_id)
        if block is not None and task_index is not None:
            current_task = block['tasks'][task_index]
            title = current_task['title']
            description = current_task['description']
            return self.edit_task(task_id, title, description, completed)
        return False

    def find_task(self, task_id):
        for block in reversed(self.chain):
            for task_index, task in enumerate(block['tasks']):
                if task['id'] == task_id and not task.get('deleted', False):
                    return block, task_index
        return None, None

    def get_next_task_id(self):
        max_id = 0
        for block in self.chain:
            for task in block['tasks']:
                if task['id'] > max_id:
                    max_id = task['id']
        return max_id + 1

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
        return guess_hash[: 4] == "0000"

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'index.html')

@app.route('/tasks', methods=['POST'])
def new_task():
    values = request.get_json()
    title = values.get('title')
    description = values.get('description')
    if title is None or description is None:
        return 'Error: Please supply a valid title and description', 400
    index = blockchain.new_task(title, description)
    response = {'message': f'Task will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    values = request.get_json()
    title = values.get('title')
    description = values.get('description')
    completed = values.get('completed')
    if blockchain.edit_task(task_id, title, description, completed):
        response = {'message': f'Task {task_id} has been updated'}
        return jsonify(response), 200
    return jsonify({'error': 'Invalid task ID'}), 400

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if blockchain.delete_task(task_id):
        response = {'message': f'Task {task_id} has been deleted'}
        return jsonify(response), 200
    return jsonify({'error': 'Invalid task ID'}), 400

@app.route('/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    values = request.get_json()
    completed = values.get('completed')
    if completed is None:
        return 'Error: Please supply a valid status', 400
    if blockchain.update_task_status(task_id, completed):
        response = {'message': f'Task {task_id} status has been updated'}
        return jsonify(response), 200
    return jsonify({'error': 'Invalid task ID'}), 400

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'tasks': block['tasks'],
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

@app.route('/check_chain', methods=['GET'])
def check_chain():
    is_valid = blockchain.is_chain_valid()
    if is_valid:
        return jsonify({'message': 'Chain is valid'})
    else:
        return jsonify({'message': 'Chain is not valid'})

if __name__ == '__main__':
    app.run(debug=True)
