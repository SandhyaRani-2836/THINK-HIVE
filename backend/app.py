from flask import Flask
from database import init_db  # Import the database initialization from the database folder
from backend.config import Config  # Import configuration settings from the config.py file

# Create the Flask app
app = Flask(__name__)

# Load the configuration settings
app.config.from_object(Config)

# Initialize the database
init_db(app)

# Run the app in debug mode
if __name__ == "__main__":
    app.run(debug=True)  # Set to True for development purposes; False in production
