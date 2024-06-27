from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                      id INTEGER PRIMARY KEY,
                      username TEXT NOT NULL,
                      password TEXT NOT NULL
                      )''')
    conn.commit()
    conn.close()

create_user_table()
def create_car_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
                      id INTEGER PRIMARY KEY,
                      mark TEXT NOT NULL,
                      model TEXT NOT NULL,
                      year INTEGER NOT NULL
                      )''')
    conn.commit()
    conn.close()

create_car_table()
def authenticate(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully."})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if authenticate(username, password):
        return jsonify({"message": "Login successful."})
    else:
        return jsonify({"error": "Invalid username or password."})

@app.route('/add_car', methods=['POST'])
def add_car():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    mark = data['mark']
    model = data['model']
    year = data['year']
    if authenticate(username, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO cars (mark, model, year) VALUES (?, ?, ?)", (mark, model, year))
            conn.commit()
            conn.close()
            return jsonify({"message": "Car added successfully."})
        except sqlite3.Error as e:
            conn.close()
            return jsonify({"error": str(e)})
    else:
        return jsonify({"error": "Authentication failed."})

@app.route('/get_cars', methods=['POST'])
def get_cars():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if authenticate(username, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cars")
        cars = cursor.fetchall()
        conn.close()
        cars_list = []
        for car in cars:
            car_dict = {
                "id": car[0],
                "mark": car[1],
                "model": car[2],
                "year": car[3]
            }
            cars_list.append(car_dict)
        return jsonify(cars_list)
    else:
        return jsonify({"error": "Authentication failed."})

if __name__ == '__main__':
    app.run(debug=True)
