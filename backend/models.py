from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_title = db.Column(db.String(200), nullable=False)
    abstract_link = db.Column(db.String(200))  # Link to the abstract file
    department = db.Column(db.String(100))  # Department of the project
    domain = db.Column(db.String(100))  # Domain of the project
    member1_name = db.Column(db.String(150))  # Name of member 1
    member1_roll_number = db.Column(db.String(50))  # Roll number of member 1
    member1_email = db.Column(db.String(120))  # Email of member 1
    member2_name = db.Column(db.String(150))  # Name of member 2 (optional)
    member2_roll_number = db.Column(db.String(50))  # Roll number of member 2
    member2_email = db.Column(db.String(120))  # Email of member 2
    member3_name = db.Column(db.String(150))  # Name of member 3 (optional)
    member3_roll_number = db.Column(db.String(50))  # Roll number of member 3
    member3_email = db.Column(db.String(120))  # Email of member 3
    member4_name = db.Column(db.String(150))  # Name of member 4 (optional)
    member4_roll_number = db.Column(db.String(50))  # Roll number of member 4
    member4_email = db.Column(db.String(120))  # Email of member 4
    member5_name = db.Column(db.String(150))  # Name of member 5 (optional)
    member5_roll_number = db.Column(db.String(50))  # Roll number of member 5
    member5_email = db.Column(db.String(120))  # Email of member 5
    hardware_filename = db.Column(db.String(200))  # Hardware requirements file
    code_link = db.Column(db.String(200))  # Link to the code repository (e.g., GitHub)
    feedback = db.Column(db.Text)  # Faculty feedback on the project
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to the User table

    def _repr_(self):
        return f'<Project {self.project_title}>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Flag for email verification
    projects = db.relationship('Project', backref='owner', lazy=True)  # Relationship with projects

    def _repr_(self):
        return f'<User {self.username}>'
