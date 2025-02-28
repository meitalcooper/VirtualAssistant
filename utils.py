"""
Utility functions shared across the Voice Assistant application.
Contains helper functions that support both API and Twilio routes:
- User information lookup (linfo)
- Password/token generation and hashing
- Other shared helper functions
These utilities provide common functionality used throughout the application.
"""
from flask import current_app
from app import create_app, db, bcrypt
from models import User
from flask_bcrypt import Bcrypt
import random
import string
from models import User



def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits  # Letters and numbers
    temp_password = ''.join(random.choice(alphabet) for i in range(length))
    return temp_password

def generate_password_hasshed(user):
    temp_password = generate_password()
    password_hash = bcrypt.generate_password_hash(temp_password)
    user.password_hashed = password_hash
    db.session.commit()
    return temp_password


def linfo(username):
    with current_app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            username = user.username
            first_name = user.first_name
            last_name = user.last_name
            full_name = f"{first_name} {last_name}"
            manager = user.manager
            uid = user.uid
            location = user.country
            hire_date = str(user.hire_date)
            return {
                "first_name": first_name,
                "full_name": full_name,
                "uid": uid,
                "manager": manager,
                "location": location,
                "hire_date": hire_date
            }
        return False






    