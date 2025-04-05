from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'THINK HIVE'

if __name__ == "__main__":
    app.run(debug=True)
