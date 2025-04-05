from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html')  # Link to your HTML front-end file

# Route for project verification
@app.route('/verify_project', methods=['POST'])
def verify_project():
    if request.method == 'POST':
        # Retrieve project details from the form
        project_name = request.form['project_name']
        project_description = request.form['project_description']
        # You can add the logic to save this data to the database here
        return redirect(url_for('home'))  # Redirect back to the home page or show success
    return render_template('verify_project.html')  # Add an HTML form to verify the project

# Route for submitting code
@app.route('/submit_code', methods=['POST'])
def submit_code():
    if request.method == 'POST':
        # Process code submission
        code = request.form['code']
        # Save the code to the database, if required
        return redirect(url_for('home'))  # Redirect back to the home page or success
    return render_template('submit_code.html')  # HTML form for code submission

if __name__ == "__main__":
    app.run(debug=True)
