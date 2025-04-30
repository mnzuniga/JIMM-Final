from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    bio = db.Column(db.String(300))
    pfp = db.Column(db.String(300))
    security_question = db.Column(db.String(200))
    security_answer = db.Column(db.String(200))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300))
    text = db.Column(db.String(300))
    datetime = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    type = db.Column(db.Boolean)  # like or comment
    extra = db.Column(db.String(300))

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2 = db.Column(db.Integer, db.ForeignKey('user.id'))
