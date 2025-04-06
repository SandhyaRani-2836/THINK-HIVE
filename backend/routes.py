from flask import Blueprint, request, jsonify, render_template
from models import db, Project

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('index.html')

@routes.route('/submit', methods=['POST'])
def submit_project():
    data = request.get_json()
    project = Project(
        student_name=data['student_name'],
        department=data['department'],
        title=data['title'],
        problem_statement=data['problem_statement'],
        drawbacks=data.get('drawbacks'),
        code_link=data.get('code_link')
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"message": "Project submitted successfully!"})
