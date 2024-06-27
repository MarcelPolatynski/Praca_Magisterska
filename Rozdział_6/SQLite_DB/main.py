from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(300), nullable=False)

    def as_dict(self):
        return {'id': self.id, 'file_name': self.file_name, 'file_type': self.file_type, 'file_size': self.file_size}

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, ''), 'index.html')

@app.route('/files', methods=['GET'])
def get_files():
    files = File.query.all()
    return jsonify([file.as_dict() for file in files])

@app.route('/files', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        file_name = file.filename
        file_type = file.content_type
        file_size = len(file.read())
        file.seek(0)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)
        new_file = File(file_name=file_name, file_type=file_type, file_size=file_size, file_path=file_path)
        db.session.add(new_file)
        db.session.commit()
        return jsonify(new_file.as_dict()), 201

@app.route('/files/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.file_name)

@app.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    os.remove(file.file_path)
    db.session.delete(file)
    db.session.commit()
    return f'File deleted {file_id}', 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
