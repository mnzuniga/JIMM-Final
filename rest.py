import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from models import User, Post, Poll, Interaction, Follow
from utils import hash_password, verify_password, allowed_file

def init_app(app):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # the normal url will lead to the main feed! 
    @app.route('/')
    @login_required
    def main_feed():
        posts = Post.query.order_by(Post.date_time.desc()).all()
        return render_template('mainfeed.html', posts=posts)


    # Feel free to change the request form name
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            usern = request.form.get('inputusername')
            passw = request.form.get('inputpassword')
            user = User.query.filter_by(username=usern).first()
            if user and verify_password(user.password, passw):
                login_user(user)
                return redirect(url_for('main_feed'))
            flash('Invalid credentials', '!!!')
        return render_template('login.html')


    # call when logging out
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))


    # for new users, using login.html? unsure
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            usern = request.form.get('inputusername')
            passw = request.form.get('inputpassword')
            if User.query.filter_by(username=usern).first():
                flash('Username alr taken', 'warning')
            else:
                user = User(
                    username=usern,
                    password=hash_password(passw)
                )
                db.session.add(user)
                db.session.commit()
                flash('Account created!', 'success')
                return redirect(url_for('login'))
        return render_template('login.html')
    

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
            flash('Profile updated!!', 'success')
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
                flash('Upload img', 'warning')
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
            results = User.query.filter(
                User.username.ilike(f'%{query}%')
            ).all()
        return render_template('search.html', results=results)


    # so i dont really know where we will put this so i said something.html lol
    # should handle poll choice and poll results
    @app.route('/polls', methods=['GET', 'POST'])
    @login_required
    def polls():
        poll = Poll.query.order_by(Poll.start_date.desc()).first() # latest
        if not poll:
            flash('No poll..', 'info')
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
        votes1 = Interaction.query.filter_by(poll_id=poll.id, interaction_type='vote',extra_info='1').count()
        votes2 = Interaction.query.filter_by(poll_id=poll.id,interaction_type='vote',extra_info='2').count()

        return render_template('something.html', poll=poll,votes1=votes1, votes2=votes2)
