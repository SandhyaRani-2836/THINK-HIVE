from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from dotenv import load_dotenv
from flask_login import current_user, login_required
import mimetypes
from flask import send_file,abort
from your_app.models import Project,User 
# from your_app import db  # Import the 'db' object from your app module
# from your_app.models import Project  # Import the Project model from your models module
from flask import send_from_directory
from urllib.parse import unquote
import mysql.connector
import os
import traceback
import re
import zipfile
from docx import Document
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(_name_)
app.secret_key = os.getenv('SECRET_KEY')  # Use the secret key from environment variable
app.debug = True

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

# Token Serializer
serializer = Serializer(app.secret_key)

# Upload Folder Config
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#app.config['UPLOAD_FOLDER'] = 'D:/Mini project-1/backend-flask/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 5*1024*1024*1024  # 100MB limit
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'zip', 'rar', 'jpg', 'png', 'py', 'cpp', 'java', 'html', 'css', 'js','jpeg'}

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'password@123'),
        database=os.getenv('DB_NAME', 'thinkhive')
    )


def read_docx(file_path):
    document = Document(file_path)
    content = ""
    for para in document.paragraphs:
        content += f"<p>{para.text}</p>"
    return content

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

# Routes
@app.route('/')
def home():
    return redirect('/signup')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        flash("Already logged in!")
        return redirect('/student_dashboard' if session['role'] == 'student' else '/faculty_dashboard')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if not is_valid_email(email):
            flash("Invalid email format.", 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already in use.", 'danger')
                return render_template('signup.html')

            # Insert new user into database
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                           (username, email, hashed_password, role))
            db.commit()

            session['user_id'] = cursor.lastrowid
            session['email'] = email
            session['role'] = role

            flash("Signup successful!")
            return redirect('/faculty_dashboard' if role == 'faculty' else '/student_dashboard')

        except Exception as e:
            flash(f"Signup error: {str(e)}", 'danger')
            db.rollback()
        finally:
            db.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        flash("Already logged in!")
        return redirect(url_for('faculty_dashboard') if session['role'] == 'faculty' else url_for('student_dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not is_valid_email(email):
            flash("Invalid email format.", 'danger')
            return render_template('login.html')

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], password):
                flash("Invalid credentials.", 'danger')
                return render_template('login.html')

            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            # flash("Login successful!")

            return redirect(url_for('faculty_dashboard') if user['role'] == 'faculty' else url_for('student_dashboard'))

        except Exception as e:
            flash(f"Login error: {str(e)}", 'danger')
        finally:
            if db:
                db.close()

    return render_template('login.html')

# Forgot password route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if not is_valid_email(email):
            flash("Invalid email format.", 'danger')
            return render_template('forgot_password.html')

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                token = serializer.dumps(email, salt='reset-password')
                reset_url = url_for('reset_password', token=token, _external=True)

                msg = Message('Password Reset', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'Click here to reset your password: {reset_url}'
                mail.send(msg)

                flash("Reset link sent to your email!", 'success')
                return redirect('/login')
            else:
                flash("Email not found.", 'danger')

        except Exception as e:
            flash(f"Error sending email: {str(e)}", 'danger')
        finally:
            db.close()

    return render_template('forgot_password.html')

# Reset password route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='reset-password', max_age=3600)
    except Exception:
        flash("Reset link is invalid or expired.", 'danger')
        return redirect('/login')

    if request.method == 'POST':
        new_password = request.form['new_password']
        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", 'danger')
            return render_template('reset_password.html')

        hashed_password = generate_password_hash(new_password)

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            db.commit()
            flash("Password reset successful!", 'success')
            return redirect('/login')
        except Exception as e:
            flash(f"Password reset error: {str(e)}", 'danger')
            db.rollback()
        finally:
            db.close()

    return render_template('reset_password.html')


@app.route('/upload_project', methods=['GET', 'POST'])
def upload_project():
    if 'email' not in session or session.get('role') != 'student':
        flash('Login required.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            form = request.form
            files = request.files

            student_email = session.get('email')

            # Collect all member details (up to 5)
            members = []
            for i in range(1, 6):
                name = form.get(f'member{i}_name', '').strip()
                roll = form.get(f'member{i}_roll', '').strip()
                email = form.get(f'member{i}_email', '').strip()
                members.append((name, roll, email))

            project_title = form.get('project_title', '').strip()
            domain = form.get('domain', '').strip()
            department = form.get('department', '').strip()

            abstract_file = files.get('abstract_file')
            hardware_req_file = files.get('hardware_req_file')
            hardware_req_link = form.get('hardware_req_link', '').strip()
            code_link = form.get('code_link', '').strip()
            project_zip = files.get('project_folder')

            # Validation
            if not project_title or not members[0][0] or not members[0][1] or not domain or not department:
                flash("Missing required fields.", 'danger')
                return render_template('upload_project.html')

            if not abstract_file or not allowed_file(abstract_file.filename):
                flash('Invalid or missing abstract file.', 'danger')
                return render_template('upload_project.html')

            if not project_zip or not allowed_file(project_zip.filename):
                flash('Invalid or missing project folder file.', 'danger')
                return render_template('upload_project.html')

            # Save files
            abstract_filename = secure_filename(abstract_file.filename)
            abstract_filepath = os.path.join(app.config['UPLOAD_FOLDER'], abstract_filename)
            abstract_file.save(abstract_filepath)

            project_folder_filename = secure_filename(project_zip.filename)
            project_folder_filepath = os.path.join(app.config['UPLOAD_FOLDER'], project_folder_filename)
            project_zip.save(project_folder_filepath)

            hardware_req_filename = ''
            if hardware_req_file and allowed_file(hardware_req_file.filename):
                hardware_req_filename = secure_filename(hardware_req_file.filename)
                hardware_req_filepath = os.path.join(app.config['UPLOAD_FOLDER'], hardware_req_filename)
                hardware_req_file.save(hardware_req_filepath)

            # SQL Insert (storing relative paths)
            cursor.execute("""
                INSERT INTO projects (
                    member1_name, member1_roll, member1_email,
                    member2_name, member2_roll, member2_email,
                    member3_name, member3_roll, member3_email,
                    member4_name, member4_roll, member4_email,
                    member5_name, member5_roll, member5_email,
                    project_title, domain, department,
                    abstract_file, project_folder,
                    hardware_req_file, hardware_req_link, code_link
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                *members[0], *members[1], *members[2], *members[3], *members[4],
                project_title, domain, department,
                os.path.join('uploads', abstract_filename),  # Store relative path
                os.path.join('uploads', project_folder_filename),
                os.path.join('uploads', hardware_req_filename) if hardware_req_filename else '',
                hardware_req_link, code_link
            ))

            db.commit()
            flash("Project uploaded successfully!", "success")
            return redirect('/student_dashboard')

        except Exception as e:
            print("Upload Error:", e)
            traceback.print_exc()
            flash(f"Error uploading project: {str(e)}", "danger")
        finally:
            if db:
                db.close()

    return render_template('upload_project.html')

# Route to handle student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    return render_template('student_dashboard.html')

@app.route('/faculty_dashboard', methods=['GET'])
def faculty_dashboard():
    if session.get('role') != 'faculty' or not session.get('user_id'):
        flash('Unauthorized access. Please login first.', 'danger')
        return redirect('/login')

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch projects along with latest feedback if available
        cursor.execute("""
            SELECT 
                p.id, p.project_title, p.domain, p.department,
                p.member1_name, p.member1_roll, p.member1_email,
                p.member2_name, p.member2_roll, p.member2_email,
                f.feedback_text as feedback
            FROM projects p
            LEFT JOIN (
                SELECT project_id, feedback_text
                FROM feedback
                ORDER BY id DESC
            ) f ON p.id = f.project_id
        """)
        projects = cursor.fetchall()

        # Handle missing details
        for project in projects:
            if not project['member1_name']:
                project['member1_name'] = 'No name available'
            if not project['member1_roll']:
                project['member1_roll'] = 'No roll number available'
            if not project['member1_email']:
                project['member1_email'] = 'No email available'
            if not project['member2_name']:
                project['member2_name'] = 'No name available'
            if not project['member2_roll']:
                project['member2_roll'] = 'No roll number available'
            if not project['member2_email']:
                project['member2_email'] = 'No email available'

        return render_template('faculty_dashboard.html', projects=projects)

    except Exception as e:
        flash(f"Error fetching projects: {str(e)}", 'danger')
        return redirect(url_for('faculty_dashboard'))

    finally:
        if db:
            db.close()

@app.route('/give_feedback', methods=['POST'])
def give_feedback():
    if session.get('role') != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        project_id = request.form.get('project_id')
        feedback_text = request.form.get('feedback')

        if not feedback_text.strip():
            flash('Feedback cannot be empty.', 'danger')
            return redirect(url_for('faculty_dashboard'))

        # Feedback length validation
        if len(feedback_text.strip()) < 10:
            flash('Feedback should be at least 10 characters long.', 'danger')
            return redirect(url_for('faculty_dashboard'))

        # Insert into feedback table
        cursor.execute("""
            INSERT INTO feedback (project_id, faculty_id, feedback_text)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE feedback_text = VALUES(feedback_text)
        """, (project_id, session['user_id'], feedback_text))
        db.commit()

        # flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))

    except Exception as e:
        flash(f"Error submitting feedback: {str(e)}", 'danger')
        return redirect(url_for('faculty_dashboard'))

    finally:
        if db:
            db.close()

@app.route('/project_details/<int:project_id>')
def project_details(project_id):
    # Fetch the project from the database
    project = Project.query.get(project_id)

    # If the project is not found, redirect to the view_projects page with an error message
    if not project:
        flash("Project not found!", "danger")
        return redirect(url_for('view_projects'))

    # Fetch related project files from the database, if applicable
    # For example, files associated with the project might be stored in a 'files' table
    files_list = []  # Fetch project files associated with the project
    for file in project.files:
        files_list.append({
            'filename': file.filename,
            'filepath': file.filepath,
            'filetype': file.filetype
        })

    # Optionally, fetch feedback for the project if available
    feedback = project.feedback  # Assuming you have a feedback field in the Project model
    if feedback:
        feedback = feedback.text  # Or however feedback is stored in your model

    # You can also include other details like a list of members, project title, etc.
    project_details = {
        'title': project.title,
        'description': project.description,
        'members': project.members,  # Assuming the project has an associated list of members
        'feedback': feedback,
    }

    # Render the project details page with all the necessary data
    return render_template('project_details.html', project=project_details, files_list=files_list)

@app.route('/view_projects', methods=['GET'])
def view_projects():
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()

        return render_template('view_projects.html', projects=projects)  # Make sure this is view_projects.html

    except Exception as e:
        flash(f"Error fetching projects: {str(e)}", 'danger')
        return redirect(url_for('faculty_dashboard'))

    finally:
        if db:
            db.close()

@app.route('/view_project_details/<int:project_id>', methods=['GET'])
def view_project_details(project_id):
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = cursor.fetchone()

        if not project:
            # flash('Project not found!', 'danger')
            return redirect(url_for('view_projects'))
        current_user_role = session.get('role', '')
        # List of project files for display
        files_list = []

        if project.get('project_folder'):
            project_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], project['project_folder'])
            if os.path.isdir(project_folder_path):
                for root, dirs, files in os.walk(project_folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Convert the file path to use forward slashes
                        relative_path = os.path.relpath(full_path, app.config['UPLOAD_FOLDER']).replace("\\", "/")
                        files_list.append(relative_path)

        # Abstract file handling
        abstract_link = None
        if project.get('abstract_file'):
            abstract_link = url_for('view_file', filepath=project['abstract_file'].replace("\\", "/"))
            print("Generated abstract link:", abstract_link)  # Debug line
        if not abstract_link:
            # flash('Abstract file is missing.', 'warning')  # Add flash if missing
            print("Abstract file is missing.")  # Print message when abstract is missing

        # Hardware file handling
        hardware_file_link = None
        if project.get('hardware_req_file'):
            hardware_file_link = url_for('view_file', filepath=project['hardware_req_file'].replace("\\", "/"))
        if not hardware_file_link:
            # flash('Hardware requirement file is missing.', 'warning')  # Add flash if missing
            print("Hardware requirement file is missing.")  # Print message when hardware file is missing

        # Render template with the project details
        return render_template('view_project_details.html', 
                               project=project,
                               files_list=files_list,
                               abstract_link=abstract_link,
                               hardware_file_link=hardware_file_link,
                               current_user_role=current_user_role)

    except Exception as e:
        # flash(f"Error fetching project details: {str(e)}", 'danger')
        print(f"Error fetching project details: {str(e)}")  # Print the error
        return redirect(url_for('view_projects'))
    finally:
        if db:
            db.close()

        
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect('/login')

# View a file (PDF, image, or text)

from flask import request, flash, redirect, url_for, send_file, render_template
from urllib.parse import unquote
import os
import mimetypes

@app.route('/view_file/', defaults={'filepath': None})
@app.route('/view_file/<path:filepath>')
def view_file(filepath):
    project_id = request.args.get('project_id')  # Get project_id from query parameters

    if filepath is None:
        # flash("No file specified.", "danger")
        if project_id:
            return redirect(url_for('view_project_details', project_id=project_id))
        else:
            return redirect(url_for('view_projects'))

    try:
        # Decode URL-encoded filepath
        filepath = unquote(filepath)
        app.logger.debug(f"Decoded filepath: {filepath}")

        # Construct full path
        uploads_dir = app.config['UPLOAD_FOLDER']
        full_path = os.path.join(uploads_dir, filepath)
        app.logger.debug(f"Attempting to open file: {full_path}")

        if not os.path.isfile(full_path):
            app.logger.warning(f"File not found: {full_path}")
            flash("File not found.", "danger")
            return redirect(url_for('view_projects'))

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(full_path)
        app.logger.debug(f"MIME type: {mime_type}")

        # Serve PDF or image files
        if mime_type in ['application/pdf'] or (mime_type and mime_type.startswith('image')):
            app.logger.info(f"Serving PDF/image file: {full_path}")
            return send_file(full_path, mimetype=mime_type)

        # Display text/code files
        if mime_type and mime_type.startswith('text'):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            filename = os.path.basename(full_path)
            app.logger.info(f"Displaying text/code file: {filename}")
            return render_template('view_file.html', filename=filename, content=content)

        # Unsupported file type
        app.logger.warning(f"Unsupported file type for viewing: {mime_type}. Redirecting to download.")
        flash("Unsupported file type for viewing. Downloading instead.", "info")
        return redirect(url_for('download_file', filename=filepath))

    except Exception as e:
        app.logger.error(f"Error while trying to serve file {filepath}: {str(e)}")
        flash("An error occurred while trying to load the file. Please try again later.", "danger")
        return redirect(url_for('view_projects'))


@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        # Get the full file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            flash("File not found.", "danger")
            abort(404)  # Return 404 error if file not found

        # List of file extensions that should open inline in the browser
        inline_extensions = ['.pdf', '.txt', '.html', '.htm', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.java', '.css', '.js']

        # Get file extension
        ext = os.path.splitext(filename)[1].lower()

        if ext in inline_extensions:
            # Open in the browser (inline)
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

        else:
            # Force download (attachment)
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    except Exception as e:
        flash(f"Error while sending file: {e}", "danger")
        app.logger.error(f"Error while sending file {filename}: {e}")
        abort(500)  # Internal server error

@app.route('/list_uploads')
def list_uploads():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return "<br>".join(files)
    except Exception as e:
        return f"Error reading upload folder: {e}"

if _name_ == '_main_':
    app.run(debug=True, use_reloader=True)
