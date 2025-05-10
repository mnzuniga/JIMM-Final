from flask import Flask
from flask_login import LoginManager
from config import Config
from database import init_app as db_init, db
from extensions import login_manager, admin
from models import User, Post, Poll, Interaction, Follow
from rest import init_app as register_routes
from flask_admin.contrib.sqla import ModelView
from utils import hash_password


# need to put it here to fix bug??
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_init(app)
    login_manager.init_app(app)
    admin.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    register_routes(app)

    # admin function
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Poll, db.session))
    admin.add_view(ModelView(Interaction, db.session))
    admin.add_view(ModelView(Follow, db.session))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

