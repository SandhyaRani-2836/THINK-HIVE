from flask import Blueprint, request, redirect, url_for, flash
import os

routes = Blueprint('routes', _name_)

UPLOAD_FOLDER = 'uploaded_documents'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/upload', methods=['POST'])
def upload_project():
    if 'document' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['document']
    if file and allowed_file(file.filename):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Now collect other form data if needed
        name = request.form.get('name')
        department = request.form.get('department')
        title = request.form.get('title')
        statement = request.form.get('statement')
        link = request.form.get('link')
        drawbacks = request.form.get('drawbacks')

        # You can now save this data into DB (will help with that too)
        return 'Project Uploaded Successfully'
    else:
        return 'Invalid file format'

from flask import Blueprint, request, redirect, url_for, render_template

routes = Blueprint('routes', _name_)

@routes.route('/login', methods=['POST'])
def login():
    # authentication logic here (mock or real)
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == "admin" and password == "admin":  # example logic
        return redirect(url_for('routes.upload_page'))
    else:
        return "Invalid credentials"

@routes.route('/signup', methods=['POST'])
def signup():
    # collect signup info
    return redirect(url_for('routes.upload_page'))

@routes.route('/upload', methods=['GET', 'POST'])
def upload_page():
    return render_template('upload.html')  # make sure to move upload.html to 'templates' folder


from flask import Blueprint, request, redirect, url_for, render_template

routes = Blueprint('routes', _name_)

@routes.route('/')
def home():
    return render_template('login.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and password == "admin":  # Simple logic
            return redirect(url_for('routes.upload_page'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Save user info if needed
        return redirect(url_for('routes.upload_page'))
    return render_template('signup.html')

@routes.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')
