from web3 import Web3, HTTPProvider
from solcx import compile_source
from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__)

contract_source_code = '''
pragma solidity ^0.8.0;

contract AuthenticationContract {
    struct User {
        string username;
        string password;
        bool isRegistered;
    }

    mapping(address => User) public users;

    event UserRegistered(address indexed userAddress, string username);

    function register(string memory _username, string memory _password) public {
        require(!users[msg.sender].isRegistered, "User already registered");
        users[msg.sender] = User(_username, _password, true);
        emit UserRegistered(msg.sender, _username);
    }

    function login(string memory _username, string memory _password) public view returns (bool) {
        User memory user = users[msg.sender];
        return (keccak256(bytes(user.username)) == keccak256(bytes(_username)) &&
                keccak256(bytes(user.password)) == keccak256(bytes(_password)));
    }
}
'''

compiled_sol = compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:AuthenticationContract']

web3 = Web3(HTTPProvider('http://127.0.0.1:7545'))

def deploy_contract():
    contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = contract.constructor().transact()
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt.contractAddress

contract_address = deploy_contract()
contract_instance = web3.eth.contract(address=contract_address, abi=contract_interface['abi'])

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'index.html')
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    try:
        tx_hash = contract_instance.functions.register(username, password).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return jsonify({"message": "User registered successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    try:
        login_success = contract_instance.functions.login(username, password).call()
        if login_success:
            return jsonify({"message": "Login successful."})
        else:
            return jsonify({"error": "Invalid username or password."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)