from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return {'id': self.id, 'title': self.title, 'content': self.content, 'completed': self.completed}

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.as_dict() for task in tasks])

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    new_task = Task(title=data['title'], content=data['content'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.as_dict()), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.content = data.get('content', task.content)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify(task.as_dict())

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
