from flask import Flask
from routes import routes
import os

app = Flask(_name_)
app.secret_key = "thinkhive"
app.config['UPLOAD_FOLDER'] = 'uploaded_documents'

app.register_blueprint(routes)

if _name_ == "_main_":
    app.run(debug=True)
