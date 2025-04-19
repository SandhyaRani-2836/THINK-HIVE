from flask import Flask, render_template, request, jsonify
 from flask_sqlalchemy import SQLAlchemy
 from flask_cors import CORS
 import os
 from flask import Flask, render_template
 from config import Config
 from models import db
 from routes import routes
 
 app = Flask(_name_, static_folder="../frontend", template_folder="../frontend")
 app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
 app.config.from_object(Config)
 
 CORS(app)
 app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/database.db'
 app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 db = SQLAlchemy(app)
 
 from models import Project
 db.init_app(app)
 app.register_blueprint(routes)
 
 @app.route('/')
 def home():
     return render_template('index.html')
 
 @app.route('/submit', methods=['POST'])
 def submit():
     data = request.get_json()
     project = Project(
         student_name=data['student_name'],
         project_title=data['project_title'],
         department=data['department'],
         description=data['description']
     )
     db.session.add(project)
     db.session.commit()
     return jsonify({'message': 'Project submitted successfully'}), 201
     return app.send_static_file('index.html')
 
 if _name_ == '_main_':
 if __name__ == '__main__':
     with app.app_context():
         db.create_all()
     app.run(debug=True)
