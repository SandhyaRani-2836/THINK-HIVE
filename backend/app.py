from flask import Flask
from config import Config
from models import db
from routes import routes

app = Flask(_name_, static_folder=\"../frontend\", template_folder=\"../frontend\")
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(routes)

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
