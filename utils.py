import os
from werkzeug.security import generate_password_hash, check_password_hash

# these are probably fine
allowed = {'png', 'jpg', 'jpeg'}

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)

# are they normal ass files
def allowed_file(filename: str) -> bool:
    return ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed)
