# all database setup with SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# database design
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    pfp = db.Column(db.String(256))  # URL or filepath
    bio = db.Column(db.String(256))
    security_question = db.Column(db.String(256))
    security_answer = db.Column(db.String(256))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256))  # URL or path
    text = db.Column(db.Text)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), nullable=False)
    option1 = db.Column(db.String(128), nullable=False)
    option2 = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    interaction_type = db.Column(db.Boolean, nullable=False)  # True=like, False=comment
    extra_info = db.Column(db.Text)  # comment text

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class UserPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)


def init_app(app):
    db.init_app(app)
