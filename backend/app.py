# main function and initialization here

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from rest import api_routes
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Define your login route if needed

# Register RESTful API routes from `rest.py`
app.register_blueprint(api_routes)

# Ensure the database is created
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('admin/index.html')  # Example for rendering admin page

if __name__ == '__main__':
    app.run(debug=True)
