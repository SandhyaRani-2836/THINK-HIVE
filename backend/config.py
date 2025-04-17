import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'database', 'database.db')  # updated here
SECRET_KEY = 'your_secret_key'
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
