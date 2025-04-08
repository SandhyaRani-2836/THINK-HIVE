from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    topic = db.Column(db.String(120), nullable=False)
    code_link = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    submitted_by = db.Column(db.String(120), nullable=False)
