from app import create_app, db
from models import User
from utils import generate_password_hasshed
from datetime import date
from thefuzz import fuzz
from jellyfish import soundex
"""

app = create_app()

with app.app_context():
    users = User.query.filter_by(country="Israel").all()
    for user in users:
        user.email = "meitalkop12@gmail.com"
    db.session.commit()
    print(f"Updated {len(users)} Israeli users with email.")

with app.app_context():
    username = 'mecooper'
    first_name = 'Meital'
    last_name = 'Cooper'
    manager = 'Radka Mikolavka'
    country = 'Israel'
    hire_date = date(2022, 2, 1)
    email = 'meitalcooper5@gmail.com'

    new_user = User(
        username = username,
        first_name = first_name,
        last_name = last_name,
        manager = manager,
        country = country,
        hire_date = hire_date,
        email = email
        )
    db.session.add(new_user)
    generate_password_hasshed(new_user)
    db.session.commit()
    print(f"user: {new_user} added successfully")
"""
s1="meetcooper"
s2="mecooper"
print(fuzz.ratio(s1,s2))



