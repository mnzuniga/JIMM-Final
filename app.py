# main function and initialization here

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail  # Import Flask-Mail
from rest import api_routes
import os

# Initialize Flask app
app = Flask(__name__)

# Secret key for session management
app.config['SECRET_KEY'] = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Example SMTP server (Gmail)
app.config['MAIL_PORT'] = 587  # SMTP port for Gmail
app.config['MAIL_USE_TLS'] = True  # Use TLS for secure connection
app.config['MAIL_USE_SSL'] = False  # Don't use SSL
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Your email password (or app password)
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Default sender for emails

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Define your login route if needed
mail = Mail(app)  # Initialize Flask-Mail with the app

# Register RESTful API routes from `rest.py`
app.register_blueprint(api_routes)

# Ensure the database is created
with app.app_context():
    db.create_all()

# Route for rendering admin page
@app.route('/')
def index():
    return render_template('admin/index.html')  # Example for rendering admin page

if __name__ == '__main__':
    app.run(debug=True)
