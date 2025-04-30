from flask import Blueprint, request, jsonify
from models import User, Post, db
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from utils import generate_reset_token, send_reset_email  # import utility functions for token generation and email sending

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

# New Forgot Password Route
@api_routes.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    email_or_phone = request.json.get('email')  # get email or phone number from request
    
    if not email_or_phone:
        return jsonify({'message': 'Email or phone number is required'}), 400
    
    # Find user by email or phone (adjust this according to your model)
    user = User.query.filter((User.email == email_or_phone) | (User.phone == email_or_phone)).first()
    
    if user:
        # Generate reset token and send email/SMS (adjust for phone if necessary)
        token = generate_reset_token(user.email)
        send_reset_email(user.email, token)  # Modify to send SMS if needed
        return jsonify({'message': 'A password reset link has been sent to your email.'}), 200
    
    return jsonify({'message': 'Email or phone number not found'}), 404
