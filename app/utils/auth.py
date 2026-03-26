import jwt 
import time
import os
import bcrypt

from ..db.users import get_email_address_from_user_id, reset_streak_if_expired
from .streak import format_streak

# Cookies expire in 48 hours
COOKIE_EXPIRY_TIME = int(172800)

SECRET_KEY = os.getenv("SECRET_KEY")

def validateSignupData(email_address, password):
    # Check that the password is an appropriate length
    if (len(password) < 8):
        return False
    
    # Check whether the inputs are empty
    if (email_address == "" or password == ""):
        return False
    
    return True

def hash_password(password):
    # Hash the password using bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_jwt_token(user_id):
    # Get the current timestamp (in SECONDS)
    current_time = int(time.time())

    # Set the expiration time to 48 hours from now
    expiration_time = current_time + COOKIE_EXPIRY_TIME

    # Create a new JWT token
    token = jwt.encode({"user-id": user_id, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")

    return token

def decode_jwt_token(token):
    try:
        # Decode JWT token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Token is valid")
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return {"error": "expired_token"}
    except jwt.InvalidTokenError:
        print("Invalid token")
        return {"error": "invalid_token"}
    
def authenticate_user(token):
    decoded_token = decode_jwt_token(token)
    if ("error" in decoded_token):
        return False
    else:
        return True
    
    # app/utils/auth.py
def get_authenticated_user(request):
    """Returns (user_id, email, streak) if authenticated, else None"""
    if "token" not in request.cookies:
        return None
    decoded = decode_jwt_token(request.cookies["token"])
    if "user-id" not in decoded:
        return None
    user_id = decoded["user-id"]
    email = get_email_address_from_user_id(user_id)
    streak = reset_streak_if_expired(user_id)
    if not email or streak is None:
        return None
    return user_id, email, format_streak(streak)