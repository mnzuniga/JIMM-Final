from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from extensions import db, login_manager, mail, admin
from models import User, Post  # Make sure these models exist
from rest import api_routes  # Ensure rest.py doesn't import app.py to avoid circular import
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Make sure this folder exists

# Flask-Mail config
# i dont think we can email :(
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password_or_app_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
login_manager.login_view = 'login'  # Replace with your login route name
admin.init_app(app)

# Register REST API routes (blueprint)
app.register_blueprint(api_routes)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Home route (Admin dashboard or landing)
#@app.route('/')
#def index():
#    return render_template('admin/index.html')
# this is not how admin works :pensive:


# simple log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid")
    
    return render_template('login.html')

# Upload post/photo route
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        photo = request.files['photo']
        description = request.form.get('description')
        tags = request.form.get('tags')
        link = request.form.get('link')

        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

            # Create new Post entry
            new_post = Post(
                user_id=current_user.id,
                photo_url=filename,
                description=description,
                tags=tags,
                link=link
            )
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('feed'))  # Replace 'feed' with your actual feed route

    return render_template('upload.html')

# User search route
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    results = None
    if query:
        results = User.query.filter(User.username.ilike(f"%{query}%")).all()
    return render_template('search.html', results=results)

#@app.route('/api/posts')
#def get_posts():
    #posts = Post.query.all()  # Fetch posts from the database
    #return jsonify([post.to_dict() for post in posts])  # Convert posts to dictionary format

if __name__ == '__main__':
    app.run(debug=True)

