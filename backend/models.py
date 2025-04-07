from app import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    project_title = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
