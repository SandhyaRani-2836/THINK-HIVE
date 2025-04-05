from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html', project_name="THINK HIVE")

# Route for project verification
@app.route('/verify_project', methods=['POST'])
def verify_project():
    if request.method == 'POST':
        project_name = "THINK HIVE"
        project_description = request.form['project_description']
        # You can add the logic to save this data to the database here
        return redirect(url_for('home'))
    return render_template('verify_project.html', project_name="THINK HIVE")

# Route for submitting code
@app.route('/submit_code', methods=['POST'])
def submit_code():
    if request.method == 'POST':
        code = request.form['code']
        # Save the code to the database, if required
        return redirect(url_for('home'))
    return render_template('submit_code.html', project_name="THINK HIVE")

if __name__ == "__main__":
    app.run(debug=True)
