from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from database import init_app as db_init, db
from extensions import login_manager, admin, SecureModelView
from models import User, Post, Poll, Interaction, Follow
from flask_admin.contrib.sqla import ModelView
from utils import hash_password, verify_password, allowed_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os

login_manager = LoginManager()
login_manager.login_view = 'login_view'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# start of flask admin stuff
class PollAdmin(SecureModelView):
    form_excluded_columns = ('interactions', 'start_date')
# end of admin stuff

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_init(app)
    login_manager.init_app(app)
    admin.init_app(app)

    admin.add_view(PollAdmin(Poll, db.session, name='Polls'))

    # Login route
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/login', methods=['GET', 'POST'])
    def login_view():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            # added by marian
            user = User.query.filter_by(username=username).first()
            if user and verify_password(user.password, password):
                login_user(user)
                if user.is_admin:
                    return redirect(url_for('admin.index'))
                return redirect(url_for('main_feed'))
            # end
            # return f"Login attempted for: {username}"
        flash('Invalid...', 'error')
        return render_template('login.html')

    # Register route
    @app.route('/register', methods=['GET', 'POST'])
    def register_view():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            question = request.form['question']
            answer = request.form['answer']
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'warning')
                return redirect(url_for('register_view'))
            
            user = User(username=username,password=hash_password(password), pfp = None, bio='', security_question = question, security_answer = answer, is_admin = False)
            db.session.add(user)
            db.session.commit()
            flash('Account created!', 'success')
            return redirect(url_for('login_view'))
        return render_template('register.html')
    
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # for images
    @app.route('/feed')
    @login_required
    def main_feed():
        posts = Post.query.order_by(Post.date_time.desc()).all()
        return render_template('mainfeed.html', posts=posts)

    # call when logging out
    @app.route('/logout')
    @login_required
    def logout_view():
        logout_user()
        return redirect(url_for('login_view'))

    # access all ur stuff, feel free to change the request forms. Also check out if you have a request file
    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            bio = request.form.get('bio')
            current_user.bio = bio
            file = request.files.get('photo')
            if file and allowed_file(file.filename):
                fn = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
                file.save(path)
                current_user.pfp = fn
            db.session.commit()
            flash('Profile updated!', 'success')
            return redirect(url_for('profile', username=current_user.username))
        return render_template('editprofile.html')

    #shows a profile given a username. pls provide
    @app.route('/profile/<username>')
    @login_required
    def profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        posts = user.posts
        return render_template('profile.html', user=user, posts=posts)


    # for uploading. this is a file request
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        if request.method == 'POST':
            file = request.files.get('photo')
            if not (file and allowed_file(file.filename)):
                flash('Please upload an image.', 'warning')
                return redirect(request.url)
            fn = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            file.save(save_path)
            text = request.form.get('description') or ''
            post = Post(image=fn, text=text)
            post.authors.append(current_user)
            db.session.add(post)
            db.session.commit()
            flash('Posted!', 'success')
            return redirect(url_for('main_feed'))
        return render_template('upload.html')

    # searches users :3
    @app.route('/search', methods=['GET'])
    @login_required
    def search():
        query = request.args.get('query', '')
        results = []
        if query:
            results = User.query.filter(User.username.ilike(f'%{query}%')).all()
        return render_template('search.html', results=results)
    
    # should handle poll choice and poll results
    @app.route('/polls', methods=['GET', 'POST'])
    @login_required
    def polls():
        poll = Poll.query.order_by(Poll.start_date.desc()).first()
        if not poll:
            flash('No polls available.', 'info')
            return redirect(url_for('main_feed'))
        
        # feel free to change form request name
        if request.method == 'POST':
            choice = request.form.get('choice')
            vote = Interaction(user_id=current_user.id, poll_id=poll.id, interaction_type='vote', extra_info=choice)
            db.session.add(vote)
            db.session.commit()
            flash('Choice saved!', 'success')
            return redirect(url_for('main_feed'))

        # count
        votes1 = Interaction.query.filter_by(poll_id=poll.id, interaction_type='vote', extra_info='1').count()
        votes2 = Interaction.query.filter_by(poll_id=poll.id, interaction_type='vote', extra_info='2').count()
        return render_template('polls.html', poll=poll, votes1=votes1, votes2=votes2
        )


    return app  # make sure this is indented properly and ends create_app()

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        initial_users = [
            {'id': 1, 'username': 'marian', 'password': 'jimmfinal', 'is_admin': True},
            {'id': 2, 'username': 'javier', 'password': 'jimmfinal', 'is_admin': False},
            {'id': 3, 'username': 'mabel',  'password': 'jimmfinal', 'is_admin': False},
            {'id': 4, 'username': 'ishita', 'password': 'jimmfinal', 'is_admin': False},
        ]
        for usern in initial_users:
            if not User.query.get(usern['id']):
                user = User(id=usern['id'],
                    username=usern['username'],
                    password=hash_password(usern['password']),
                    pfp='happy.png',
                    bio='',
                    security_question="who's your favorite professor?",
                    security_answer='hepworth',
                    is_admin=usern['is_admin'])
                db.session.add(user)

        db.session.commit()

        # initial post
        javier = User.query.filter_by(username='javier').first()
        if javier:
            existing = Post.query.filter_by(text="wow! wouldn't it be cool if this was the first post?").first()
            if not existing:
                post = Post(
                    image='happy.png',
                    text="wow! wouldn't it be cool if this was the first post?",
                    date_time=datetime.utcnow())
                post.authors.append(javier)
                db.session.add(post)
                db.session.commit()
            else:
                post = existing

            # likes
            ishita = User.query.filter_by(username='ishita').first()
            if ishita and not Interaction.query.filter_by(
                    user_id=ishita.id,
                    post_id=post.id,
                    interaction_type='like').first():
                like = Interaction(
                    user_id=ishita.id,
                    post_id=post.id,
                    interaction_type='like',
                    extra_info='')
                db.session.add(like)
                db.session.commit()

        # initial poll
        poll = Poll.query.filter_by(question="who's a better companion").first()
        if not poll:
            poll = Poll(
                question="who's a better companion",
                option1='dogs',
                option2='cats',
                start_date=datetime.utcnow())
            db.session.add(poll)
            db.session.commit()

        # poll votes init
        mapping = {
            'javier': '2',
            'ishita': '1',
            'mabel':  '1',
        }
        for usename, choice in mapping.items():
            user = User.query.filter_by(username=usename).first()
            if user and not Interaction.query.filter_by(
                    user_id=user.id,
                    poll_id=poll.id,
                    interaction_type='vote'
                ).first():
                vote = Interaction(
                    user_id=user.id,
                    poll_id=poll.id,
                    interaction_type='vote',
                    extra_info=choice
                )
                db.session.add(vote)
        db.session.commit()

        # follows
        mabel = User.query.filter_by(username='mabel').first()
        ishita = User.query.filter_by(username='ishita').first()
        if mabel and ishita:
            if not Follow.query.filter_by(follower_id=mabel.id, followed_id=ishita.id).first():
                db.session.add(Follow(follower_id=mabel.id, followed_id=ishita.id))
            if not Follow.query.filter_by(follower_id=ishita.id, followed_id=mabel.id).first():
                db.session.add(Follow(follower_id=ishita.id, followed_id=mabel.id))
        db.session.commit()

    app.run(debug=True, port=5001)
