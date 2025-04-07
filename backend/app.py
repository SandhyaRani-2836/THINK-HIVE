from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(_name_, static_folder="../frontend", template_folder="../frontend")

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Project

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    project = Project(
        student_name=data['student_name'],
        project_title=data['project_title'],
        department=data['department'],
        description=data['description']
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'message': 'Project submitted successfully'}), 201

if _name_ == '_main_':
    app.run(debug=True)
