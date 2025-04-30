from flask_mail import Message
from app import mail
import os

def send_reset_email(user_email, token):
    reset_url = f'http://localhost:5000/reset-password/{token}'
    msg = Message('Password Reset Request', recipients=[user_email])
    msg.body = f'Click the link to reset your password: {reset_url}'
    mail.send(msg)
