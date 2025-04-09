from flask import Flask
from routes import routes
import os

app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

app.secret_key = "thinkhive"
app.config['UPLOAD_FOLDER'] = 'uploaded_documents'

app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)
