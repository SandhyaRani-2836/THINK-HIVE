from flask import Flask
from routes import routes

app = Flask(_name_)
app.register_blueprint(routes)

if _name_ == '_main_':
    app.run(debug=True)
