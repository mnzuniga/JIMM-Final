from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_login import LoginManager # Removed: No longer creating a new instance here, using one from extensions
from flask_login import login_user, logout_user, login_required, current_user
from config import Config
from database import init_app as db_init, db
from extensions import login_manager, admin # Using these instances directly
from models import User, Post, Poll, Interaction, Follow
from flask_admin.contrib.sqla import ModelView
from utils import hash_password, verify_password, allowed_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid # For unique filenames

# Configure the login_manager instance imported from extensions
# This is typically done after init_app, but can be set here if login_manager is already an instance.
# However, best practice is often within create_app or an extensions setup function.
# For this fix, we'll ensure it's set correctly.
# login_manager.login_view = 'login_view' # Will be set in create_app after init

@login_manager.user_loader # Uses the login_manager instance from extensions
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError): # Handle cases where user_id might not be a valid int string
        return None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure UPLOAD_FOLDER exists - moved here to ensure app.config is loaded
    # and it's done once per app creation.
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db_init(app)
    login_manager.init_app(app) # Initialize the instance from extensions
    login_manager.login_view = 'login_view' # Set login_view after init_app
    admin.init_app(app)

    # Admin views
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Poll, db.session))
    admin.add_view(ModelView(Interaction, db.session))
    admin.add_view(ModelView(Follow, db.session))

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('main_feed'))
        return redirect(url_for('login_view'))

    @app.route('/login', methods=['GET', 'POST'])
    def login_view():
        if current_user.is_authenticated:
            return redirect(url_for('main_feed'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                flash('Username and password are required.', 'warning')
                return render_template('login.html')
            user = User.query.filter_by(username=username).first()
            if user and verify_password(user.password, password):
                login_user(user)
                return redirect(url_for('main_feed'))
            flash('Invalid credentials', 'warning')
            return render_template('login.html')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register_view():
        if current_user.is_authenticated:
            return redirect(url_for('main_feed'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Username and password are required.', 'warning')
                return render_template('register.html')
            
            # Add more validation if desired (e.g., password complexity, username format)

            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'warning')
            else:
                user = User(username=username, password=hash_password(password))
                db.session.add(user)
                db.session.commit()
                flash('Account created! Please login.', 'success')
                return redirect(url_for('login_view'))
            return render_template('register.html')
        return render_template('register.html')

    @app.route('/main_feed')
    @login_required
    def main_feed():
        page = request.args.get('page', 1, type=int)
        per_page = app.config.get('POSTS_PER_PAGE', 10)
        pagination = Post.query.order_by(Post.date_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        posts = pagination.items
        return render_template('mainfeed.html', posts=posts, pagination=pagination)

    @app.route('/logout')
    @login_required
    def logout_view():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login_view'))

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            # Change username
            new_username = request.form.get('fname')
            if new_username and new_username != current_user.username:
                if User.query.filter_by(username=new_username).first():
                    flash('Username already taken.', 'warning')
                    return redirect(url_for('edit_profile'))
                current_user.username = new_username
                flash('Username updated!', 'success')

            # Change password
            new_password = request.form.get('password')
            if new_password:
                current_user.password = hash_password(new_password)
                flash('Password updated!', 'success')

            # Change bio
            new_bio = request.form.get('bio')
            if new_bio is not None:
                current_user.bio = new_bio
                flash('Bio updated!', 'success')

            # Change profile picture
            file = request.files.get('pfpUpload')
            if file and file.filename:
                if allowed_file(file.filename):
                    original_filename = secure_filename(file.filename)
                    ext = os.path.splitext(original_filename)[1].lower()
                    unique_filename = str(uuid.uuid4()) + ext
                    path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    try:
                        file.save(path)
                        current_user.pfp = unique_filename
                        flash('Profile picture updated!', 'success')
                    except Exception as e:
                        app.logger.error(f"Failed to save profile picture: {e}")
                        flash('Failed to save profile picture due to a server error.', 'danger')
                else:
                    flash('Invalid file type for photo. Please upload an allowed image format.', 'warning')

            db.session.commit()
            return redirect(url_for('profile', username=current_user.username))
        return render_template('editprofile.html', user=current_user)


    @app.route('/profile/<username>')
    @login_required
    def profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        per_page = app.config.get('POSTS_PER_PROFILE_PAGE', 9)
        # FIX: Use Post.authors (not string) for with_parent
        pagination = Post.query.with_parent(user, Post.authors).order_by(Post.date_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        posts_on_page = pagination.items
        return render_template('profile.html', user=user, posts=posts_on_page, pagination=pagination)

    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        if request.method == 'POST':
            file = request.files.get('photo')
            text = request.form.get('description', '')
            tags = request.form.get('tags', '')
            link = request.form.get('link', '')

            if not file or not file.filename:
                flash('Please select an image file to upload.', 'warning')
                return redirect(request.url)
            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload an image.', 'warning')
                return redirect(request.url)

            original_filename = secure_filename(file.filename)
            ext = os.path.splitext(original_filename)[1].lower()
            unique_filename = str(uuid.uuid4()) + ext
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            try:
                file.save(save_path)
            except Exception as e:
                app.logger.error(f"Failed to save uploaded image: {e}")
                flash('Failed to save image due to a server error.', 'danger')
                return redirect(request.url)

            post = Post(image=unique_filename, text=text, date_time=datetime.utcnow(), tags=tags, link=link)
            post.authors.append(current_user)
            db.session.add(post)
            db.session.commit()
            flash('Posted!', 'success')
            return redirect(url_for('main_feed'))
        return render_template('upload.html')

    @app.route('/search', methods=['GET'])
    @login_required
    def search():
        query = request.args.get('query', '').strip()
        results = []
        pagination = None
        if query:
            page = request.args.get('page', 1, type=int)
            per_page = app.config.get('SEARCH_RESULTS_PER_PAGE', 10)
            pagination = User.query.filter(User.username.ilike(f'%{query}%')).paginate(page=page, per_page=per_page, error_out=False)
            results = pagination.items
        return render_template('search.html', results=results, query=query, pagination=pagination)

    @app.route('/polls', methods=['GET', 'POST'])
    @login_required
    def polls():
        poll = Poll.query.order_by(Poll.start_date.desc()).first()
        
        if not poll:
            flash('No polls available at the moment.', 'info')
            return redirect(url_for('main_feed'))

        user_vote = Interaction.query.filter_by(
            user_id=current_user.id,
            poll_id=poll.id,
            interaction_type='vote'
        ).first()

        if request.method == 'POST':
            if user_vote:
                flash('You have already voted on this poll.', 'warning')
                return redirect(url_for('polls'))

            choice = request.form.get('choice')
            
            # Validate choice. Assuming poll options are '1' and '2' for now based on vote counting.
            # Ideally, these choices ('1', '2') would come from poll.option1_value, poll.option2_value or similar.
            expected_choices = ['1', '2'] 
            if choice not in expected_choices:
                flash('Invalid choice submitted.', 'warning')
                return redirect(url_for('polls'))

            new_vote = Interaction(user_id=current_user.id, poll_id=poll.id, interaction_type='vote', extra_info=choice)
            db.session.add(new_vote)
            db.session.commit()
            user_vote = new_vote # Update user_vote status for the template
            flash('Your vote has been recorded!', 'success')
            return redirect(url_for('polls')) # Redirect to see updated results

        # Calculate votes. Consider efficiency for very popular polls (e.g., caching).
        # This assumes Poll model has option1 (text for display) and option2 (text for display)
        # And the values submitted are '1' and '2' corresponding to these options.
        votes = {
            '1': Interaction.query.filter_by(poll_id=poll.id, interaction_type='vote', extra_info='1').count(),
            '2': Interaction.query.filter_by(poll_id=poll.id, interaction_type='vote', extra_info='2').count()
        }
        
        return render_template('polls.html', poll=poll, votes=votes, user_vote=user_vote)

    # API: Get all posts (for React feed)
    @app.route('/api/posts', methods=['GET'])
    @login_required
    def api_get_posts():
        posts = Post.query.order_by(Post.date_time.desc()).all()
        result = []
        for post in posts:
            result.append({
                'id': post.id,
                'image': url_for('static', filename=f'uploads/{post.image}') if post.image else None,
                'text': post.text,
                'date_time': post.date_time.isoformat() if post.date_time else None,
                'authors': [u.username for u in post.authors],
                'likes': Interaction.query.filter_by(post_id=post.id, interaction_type='like').count(),
                'comments': [i.extra_info for i in post.interactions if i.interaction_type == 'comment']
            })
        return {'posts': result}

    # API: Like a post (toggle like/unlike)
    @app.route('/api/posts/<int:post_id>/like', methods=['POST'])
    @login_required
    def api_like_post(post_id):
        post = Post.query.get_or_404(post_id)
        existing = Interaction.query.filter_by(user_id=current_user.id, post_id=post_id, interaction_type='like').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            like_count = Interaction.query.filter_by(post_id=post_id, interaction_type='like').count()
            return {'success': True, 'liked': False, 'like_count': like_count}
        like = Interaction(user_id=current_user.id, post_id=post_id, interaction_type='like')
        db.session.add(like)
        db.session.commit()
        like_count = Interaction.query.filter_by(post_id=post_id, interaction_type='like').count()
        return {'success': True, 'liked': True, 'like_count': like_count}

    # API: Comment on a post
    @app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
    @login_required
    def api_comment_post(post_id):
        post = Post.query.get_or_404(post_id)
        comment = request.json.get('comment', '').strip()
        if not comment:
            return {'error': 'Comment required'}, 400
        new_comment = Interaction(user_id=current_user.id, post_id=post_id, interaction_type='comment', extra_info=comment)
        db.session.add(new_comment)
        db.session.commit()
        return {'success': True}

    # API: Follow a user
    @app.route('/api/follow/<username>', methods=['POST'])
    @login_required
    def api_follow_user(username):
        user = User.query.filter_by(username=username).first_or_404()
        if user.id == current_user.id:
            return {'error': 'Cannot follow yourself'}, 400
        existing = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()
        if existing:
            return {'error': 'Already following'}, 400
        follow = Follow(follower_id=current_user.id, followed_id=user.id)
        db.session.add(follow)
        db.session.commit()
        return {'success': True}

    # API: Unfollow a user
    @app.route('/api/unfollow/<username>', methods=['POST'])
    @login_required
    def api_unfollow_user(username):
        user = User.query.filter_by(username=username).first_or_404()
        follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()
        if not follow:
            return {'error': 'Not following'}, 400
        db.session.delete(follow)
        db.session.commit()
        return {'success': True}

    @app.route('/api/search/users', methods=['GET'])
    @login_required
    def api_search_users():
        query = request.args.get('query', '').strip()
        users_data = []
        if query:
            # Limit results for a modal display, can add pagination later if complex
            users = User.query.filter(User.username.ilike(f'%{query}%')).limit(10).all()
            for user in users:
                users_data.append({
                    'username': user.username,
                    'pfp': url_for('static', filename='uploads/' + user.pfp) if user.pfp else url_for('static', filename='images/default_pfp.png'), # Assuming a default pfp
                    'profile_url': url_for('profile', username=user.username)
                })
        return {'results': users_data}

    # IMPORTANT SECURITY NOTE: CSRF Protection
    # This application appears to use raw HTML forms (`request.form`) without Flask-WTF or
    # a similar CSRF protection mechanism. This makes POST endpoints vulnerable to
    # Cross-Site Request Forgery (CSRF) attacks.
    #
    # To fix this, you should:
    # 1. Integrate Flask-WTF (or another CSRF protection library).
    #    - Install it: `pip install Flask-WTF`
    #    - Add `WTF_CSRF_ENABLED = True` to your Flask `Config`.
    #    - Ensure `SECRET_KEY` is set securely in `Config`.
    # 2. Define forms using `FlaskForm` from `flask_wtf`.
    # 3. In templates, include the CSRF token, e.g., `{{ form.hidden_tag() }}` or `{{ form.csrf_token }}`.
    # 4. In your view functions, instantiate the form, pass it to the template,
    #    and use `form.validate_on_submit()` to process form data and check CSRF token.
    #
    # Example (conceptual for login):
    #
    # forms.py:
    # from flask_wtf import FlaskForm
    # from wtforms import StringField, PasswordField, SubmitField
    # from wtforms.validators import DataRequired
    # class LoginForm(FlaskForm):
    #     username = StringField('Username', validators=[DataRequired()])
    #     password = PasswordField('Password', validators=[DataRequired()])
    #     submit = SubmitField('Login')
    #
    # app.py (in login_view):
    # from forms import LoginForm
    # form = LoginForm()
    # if form.validate_on_submit():
    #     username = form.username.data
    #     password = form.password.data
    #     # ... rest of login logic
    # return render_template('login.html', form=form)
    #
    # login.html (template):
    # <form method="POST" action="{{ url_for('login_view') }}">
    #   {{ form.hidden_tag() }}  <!-- or form.csrf_token -->
    #   {{ form.username.label }} {{ form.username() }}
    #   {{ form.password.label }} {{ form.password() }}
    #   {{ form.submit() }}
    # </form>
    #
    # This is a significant change and requires modifications to forms, templates, and view logic.

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # For development only. Use migrations (e.g., Flask-Migrate) for production.
    # WARNING: debug=True is insecure and should NOT be used in a production environment.
    app.run(debug=True, port=5001)