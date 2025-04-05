from flask import Flask, render_template, send_from_directory
import os

# Adjusting paths based on your GitHub structure
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(base_dir, 'frontend')
static_dir = os.path.join(base_dir, 'frontend')

# Flask app setup
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)

# Route to serve homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve static files (like CSS, JS)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(static_dir), filename)

# Run app
if __name__ == '__main__':
    app.run(debug=True)
