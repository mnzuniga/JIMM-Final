import jwt
from datetime import datetime, timedelta
from flask_mail import Message
from extensions import mail  # Import mail from extensions.py
from config import SECRET_KEY  # Ensure SECRET_KEY is in your config

# Function to generate the reset token
def generate_reset_token(email):
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    token = jwt.encode({'email': email, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

# Function to send the reset email
def send_reset_email(email, token):
    reset_url = f"http://localhost:3000/reset-password?token={token}"  # Adjust the URL as necessary
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Click the following link to reset your password: {reset_url}'
    
    try:
        mail.send(msg)  # Send the email via Flask-Mail
    except Exception as e:
        print(f"Error sending email: {e}")
