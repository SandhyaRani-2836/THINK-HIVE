from flask import Flask 
app = Flask(_name_) 
@app.route('/') 
def home(): 
    return "Welcome to THINK-HIVE!" 
if _name_ == '_main_': 
    app.run(debug=True) 
