from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager
from config import Config
from database import init_app as db_init, db
from extensions import login_manager, admin
from models import User, Post, Poll, Interaction, Follow
from rest import init_app as register_routes
from flask_admin.contrib.sqla import ModelView
from utils import hash_password

login_manager = LoginManager()
login_manager.login_view = 'login_view'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_init(app)
    login_manager.init_app(app)
    admin.init_app(app)

    register_routes(app)

    # Admin views
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Poll, db.session))
    admin.add_view(ModelView(Interaction, db.session))
    admin.add_view(ModelView(Follow, db.session))

    # Login route
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/login', methods=['GET', 'POST'])
    def login_view():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            return f"Login attempted for: {username}"
        return render_template('login.html')

    # Register route
    @app.route('/register', methods=['GET', 'POST'])
    def register_view():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            name = request.form['name']
            return f"Registered user: {username} ({email})"
        return render_template('register.html')

    return app  # make sure this is indented properly and ends create_app()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
