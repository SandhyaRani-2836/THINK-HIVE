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
