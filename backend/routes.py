from flask import Flask, request, jsonify
from models import db, User, Project
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=data['password']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Signup successful'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/upload', methods=['POST'])
def upload_project():
    title = request.form['title']
    description = request.form['description']
    file = request.files['file']
    filename = file.filename
    upload_path = os.path.join(os.path.dirname(__file__), 'uploads', filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    file.save(upload_path)

    new_project = Project(
        title=title,
        description=description,
        code_file=filename
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'Project uploaded successfully'})

if __name__ == '__main__':
    app.run(debug=True)
