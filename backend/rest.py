# All API routes here
from flask import Blueprint, request, jsonify
from models import User, Post, db
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Create Blueprint for the API
api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

@api_routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Invalid credentials!"}), 401

@api_routes.route('/api/create_post', methods=['POST'])
def create_post():
    if not current_user.is_authenticated:
        return jsonify({"message": "Please log in to create a post!"}), 403
    
    data = request.get_json()
    content = data.get('content')
    image_url = data.get('image_url', None)
    
    new_post = Post(content=content, image_url=image_url, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully!"}), 201
