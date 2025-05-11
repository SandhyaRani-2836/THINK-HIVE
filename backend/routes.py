from flask import Blueprint

bp = Blueprint('routes', _name_)

@bp.route('/')
def home():
    return 'Hello, World!'
