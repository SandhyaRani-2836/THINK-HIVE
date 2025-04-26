app.py
from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from dotenv import load_dotenv
import mysql.connector
import os
import re
import requests
import zipfile

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(_name_)
app.secret_key = os.getenv('SECRET_KEY') or 'your_default_secret_key'
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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'zip', 'rar', 'jpg', 'png'}

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'password@123'),
        database=os.getenv('DB_NAME', 'thinkhive')
    )

# Helpers
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
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already in use.", 'danger')
                return render_template('signup.html')

            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                           (username, email, hashed_password, role))
            db.commit()

            # Check role value and ensure correct redirection
            session['user_id'] = cursor.lastrowid
            session['email'] = email
            session['role'] = role

            flash("Signup successful!")

            # Redirect to the appropriate dashboard based on role
            if role == 'faculty':
                return redirect('/faculty_dashboard')
            else:
                return redirect('/student_dashboard')

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
        # Redirect to the appropriate dashboard based on the user's role
        return redirect('/faculty_dashboard' if session['role'] == 'faculty' else '/student_dashboard')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if not is_valid_email(email):
            flash("Invalid email format.", 'danger')
            return render_template('login.html')

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                flash("Account not found.", 'danger')
            elif user['role'] != role:
                flash(f"Incorrect role! Registered as {user['role']}.", 'danger')
            elif check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['role'] = user['role']
                flash("Login successful!")

                # Redirect to the appropriate dashboard based on the user's role
                if user['role'] == 'faculty':
                    return redirect('/faculty_dashboard')
                else:
                    return redirect('/student_dashboard')
            else:
                flash("Invalid credentials.", 'danger')

        except Exception as e:
            flash(f"Login error: {str(e)}", 'danger')
        finally:
            db.close()

    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

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

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='reset-password', max_age=3600)
    except Exception:
        flash("Reset link is invalid or expired.", 'danger')
        return redirect('/login')

    if request.method == 'POST':
        new_password = request.form['new_password']
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
    if 'email' not in session:
        flash('Login required.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        try:
            db = get_db_connection()
            cursor = db.cursor()

            student_email = session.get('email')

            # Project fields
            form = request.form
            files = request.files

            member1_name = form['member1_name']
            member1_roll = form['member1_roll']
            member2_name = form.get('member2_name', '')
            member2_roll = form.get('member2_roll', '')
            member3_name = form.get('member3_name', '')
            member3_roll = form.get('member3_roll', '')
            member4_name = form.get('member4_name', '')
            member4_roll = form.get('member4_roll', '')
            member5_name = form.get('member5_name', '')
            member5_roll = form.get('member5_roll', '')
            domain = form['domain']
            department = form['department']

            abstract_file = files['abstract_file']
            hardware_req_file = files.get('hardware_req_file')
            project_folder = files.get('project_folder')

            hardware_req_link = form.get('hardware_req_link', '')
            code_link = form.get('code_link', '')

            # Save files
            if not allowed_file(abstract_file.filename):
                flash('Invalid abstract file.', 'danger')
                return render_template('upload_project.html')

            abstract_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(abstract_file.filename))
            abstract_file.save(abstract_path)

            hardware_req_path = None
            if hardware_req_file and allowed_file(hardware_req_file.filename):
                hardware_req_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(hardware_req_file.filename))
                hardware_req_file.save(hardware_req_path)

            project_folder_path = None
            if project_folder and allowed_file(project_folder.filename):
                project_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(project_folder.filename))
                project_folder.save(project_zip_path)
                extracted_folder = project_zip_path.replace('.zip', '')
                with zipfile.ZipFile(project_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_folder)
                project_folder_path = extracted_folder

            # Insert into database
            cursor.execute(""" 
                INSERT INTO projects (
                    member1_name, member1_roll, member1_email,
                    member2_name, member2_roll,
                    member3_name, member3_roll,
                    member4_name, member4_roll,
                    member5_name, member5_roll,
                    domain, department,
                    abstract_file, project_folder,
                    hardware_req_file, hardware_req_link, code_link
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                member1_name, member1_roll, student_email,
                member2_name, member2_roll,
                member3_name, member3_roll,
                member4_name, member4_roll,
                member5_name, member5_roll,
                domain, department,
                abstract_path, project_folder_path,
                hardware_req_path, hardware_req_link, code_link
            ))

            db.commit()
            flash('Project uploaded successfully!', 'success')
            return redirect('/student_dashboard')

        except Exception as e:
            flash(f'Error uploading project: {str(e)}', 'danger')
            db.rollback()
        finally:
            db.close()

    return render_template('upload_project.html')

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    return render_template('student_dashboard.html')

@app.route('/faculty_dashboard')
def faculty_dashboard():
    if session.get('role') != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    return render_template('faculty_dashboard.html')
@app.route('/give_feedback', methods=['GET', 'POST'])
def give_feedback():
    if session.get('role') != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect('/login')

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == 'POST':
            project_id = request.form['project_id']
            feedback_text = request.form['feedback']

            if not feedback_text.strip():
                flash('Feedback cannot be empty.', 'danger')
                return redirect(url_for('give_feedback'))

            # Insert feedback into the database
            cursor.execute("INSERT INTO feedback (project_id, faculty_id, feedback_text) VALUES (%s, %s, %s)",
                           (project_id, session['user_id'], feedback_text))
            db.commit()
            flash('Feedback submitted successfully!', 'success')
            return redirect(url_for('faculty_dashboard'))

        # Fetch projects for which feedback can be given
        cursor.execute("""
            SELECT p.id, p.member1_name, p.member1_roll, p.domain, p.department 
            FROM projects p 
            WHERE NOT EXISTS (
                SELECT 1 FROM feedback f WHERE f.project_id = p.id
            )
        """)
        projects = cursor.fetchall()

        if not projects:
            flash('No projects available for feedback at the moment.', 'info')

        return render_template('give_feedback.html', projects=projects)

    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
    finally:
        db.close()
@app.route('/view_projects', methods=['GET'])
def view_projects():
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()

        return render_template('view_projects.html', projects=projects)

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

        if project is None:
            flash('Project not found!', 'danger')
            return redirect(url_for('view_projects'))

        return render_template('view_project_details.html', project=project)

    except Exception as e:
        flash(f"Error fetching project details: {str(e)}", 'danger')
        return redirect(url_for('view_projects'))

    finally:
        if db:
            db.close()

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect('/login')

if _name_ == '_main_':
    app.run()
