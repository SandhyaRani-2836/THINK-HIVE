from flask import Blueprint, render_template, request, redirect, url_for

routes = Blueprint('routes', __name__)

# Landing Page
@routes.route('/')
def landing():
    return render_template('landing.html')

# Login Page (GET) and Login Form Handling (POST)
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            return redirect(url_for('routes.upload_page'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Signup Page (GET) and Signup Form Handling (POST)
@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup form data here (just redirecting now)
        return redirect(url_for('routes.upload_page'))
    return render_template('signup.html')

# Upload Page
@routes.route('/upload', methods=['GET', 'POST'])
def upload_page():
    return render_template('upload.html')
@routes.route('/view-projects')
def view_projects():
    # Dummy data (you’ll replace this with actual DB queries)
    projects = [
        {
            "name": "Alice",
            "department": "CSE",
            "domain": "AI",
            "title": "Smart Vision",
            "statement": "AI for visually impaired",
            "link": "https://github.com/alice/smartvision",
            "document": "smartvision.pdf"
        },
        {
            "name": "Bob",
            "department": "ECE",
            "domain": "IoT",
            "title": "Home Automation",
            "statement": "Smart home using sensors",
            "link": "",
            "document": "homeautomation.pdf"
        }
    ]

    department_wise = {}
    for project in projects:
        dept = project['department']
        if dept not in department_wise:
            department_wise[dept] = []
        department_wise[dept].append(project)

    return render_template('view.html', department_wise=department_wise)
