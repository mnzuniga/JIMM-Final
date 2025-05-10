from flask_login import UserMixin
from database import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    pfp = db.Column(db.String(256))
    bio = db.Column(db.String(256))
    security_question = db.Column(db.String(256))
    security_answer = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    posts = db.relationship('Post', secondary='user_posts', back_populates='authors')
    interactions = db.relationship('Interaction', back_populates='user')

    def get_id(self):
        return str(self.id)

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Poll(db.Model):
    __tablename__ = 'polls'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), nullable=False)
    option1 = db.Column(db.String(128), nullable=False)
    option2 = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)

    interactions = db.relationship('Interaction', back_populates='poll')

class Interaction(db.Model):
    __tablename__ = 'interactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=True)
    interaction_type = db.Column(db.String(50), nullable=False)
    extra_info = db.Column(db.Text)

    user = db.relationship('User', back_populates='interactions')
    post = db.relationship('Post', back_populates='interactions')
    poll = db.relationship('Poll', back_populates='interactions')

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256))
    text = db.Column(db.Text)
    date_time = db.Column(db.DateTime, default=datetime)

    interactions = db.relationship('Interaction', back_populates='post')
    authors = db.relationship('User', secondary='user_posts', back_populates='posts')