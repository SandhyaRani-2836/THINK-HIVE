from flask import Flask, render_template

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')

@app.route('/')
def home():
    return render_template('index.html', project_name="THINK HIVE")

if __name__ == '__main__':
    app.run(debug=True)
