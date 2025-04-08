from flask import Blueprint, request, jsonify
from models import db, Project

routes = Blueprint('routes', __name__)

@routes.route('/submit_project', methods=['POST'])
def submit_project():
    data = request.get_json()
    project = Project(**data)
    db.session.add(project)
    db.session.commit()
    return jsonify({'message': 'Project submitted successfully'}), 201

@routes.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([{
        'title': p.title,
        'department': p.department,
        'topic': p.topic,
        'code_link': p.code_link,
        'description': p.description,
        'submitted_by': p.submitted_by
    } for p in projects])
