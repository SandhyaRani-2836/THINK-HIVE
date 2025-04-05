from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder='frontend')

@app.route('/')
def home():
    return render_template('index.html', project_name="THINK HIVE")

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'frontend'), filename)

if __name__ == '__main__':
    app.run(debug=True)
