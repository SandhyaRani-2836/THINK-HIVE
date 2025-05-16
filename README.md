
# ThinkHive - Cloud-Based Academic Archive

ThinkHive is a cloud-based web application designed to store, manage, and showcase academic projects submitted by students across various departments.

---

## Features

- Project submission form with student and project details
- Backend built with Flask & SQLite
- API endpoints to handle project data
- Cloud-ready setup using cloud-config.yaml
- Frontend with clean UI for project uploads

---

## Folder Structure 
THINK-HIVE/
├── backend/
│ ├── app.py # Main Flask application
│ ├── config.py # Configuration settings
│ ├── models.py # Database models
│ ├── requirements.txt # Python dependencies
│ └── routes.py # API routes/endpoints
│
├── database/
│ └── database.db # SQLite database file
│
├── docs/
│ ├── API_Documentation.md # API documentation
│ └── cloud-config.yaml # Configuration for cloud deployment
│
├── frontend/
│ ├── base.html
│ ├── edit_project.html
│ ├── faculty_dashboard.html
│ ├── forgot_password.html
│ ├── give_feedback.html
│ ├── login.html
│ ├── project_details.html
│ ├── reset_password.html
│ ├── script.js
│ ├── signup.html
│ ├── student_dashboard.html
│ ├── styles.css
│ ├── upload_project.html
│ ├── view_file.html
│ ├── view_project_details.html
│ └── view_projects.html
│
├── Dockerfile # Docker configuration
├── LICENSE # Project license
├── README.md # Project introduction and setup guide
├── migrations/ # Folder for database migration files
├── setup.sh # Shell script for setup tasks
└── test/ # Test files for the backend/frontend
