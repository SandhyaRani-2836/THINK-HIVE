from flask import Flask, render_template, send_from_directory
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(base_dir, 'frontend')
static_dir = os.path.join(base_dir, 'frontend')

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(static_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
