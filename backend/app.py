from flask import Flask, render_template
from config import Config
from models import db
from routes import routes

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(routes)

@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
