from flask import Flask, render_template

# Initialize Flask app with specific static and template folder paths
app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")

# Define a route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
