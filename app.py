from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from extensions import db, login_manager, mail
from models import User, Post  # Make sure these models exist
from rest import api_routes  # Ensure rest.py doesn't import app.py to avoid circular import

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Make sure this folder exists

# Flask-Mail config
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

# Register REST API routes (blueprint)
app.register_blueprint(api_routes)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Home route (Admin dashboard or landing)
@app.route('/')
def index():
    return render_template('admin/index.html')

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

