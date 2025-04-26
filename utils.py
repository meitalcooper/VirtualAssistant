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
from jellyfish import soundex
from thefuzz import fuzz
import unicodedata
import re
import dateparser






def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits  # Letters and numbers
    temp_password = ''.join(random.choice(alphabet) for i in range(length))
    return temp_password

def generate_password_hasshed(user):
    temp_password = generate_password()
    password_hash = bcrypt.generate_password_hash(temp_password).decode('utf-8')
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

def normalize_country(country_code_or_name):
    """
    Converts country codes like 'IL' to full country names like 'Israel'
    to match database entries.
    """
    country_map = {
        "IL": "Israel",
        "US": "United States",
        "IN": "India",
        "JP": "Japan",
        "KR": "Korea",
        "CN": "China",
        "GB": "United Kingdom",
        "DE": "Germany",
        "FR": "France",
        "IT": "Italy",
        "ES": "Spain",
        "PL": "Poland",
        "CZ": "Czech Republic",
        "UA": "Ukraine",
        "BR": "Brazil",
        "MX": "Mexico",
        "AU": "Australia",
        "CA": "Canada",
        "AR": "Argentina",
        
    }

    # If already a full name, return as is
    if country_code_or_name in country_map.values():
        return country_code_or_name

    return country_map.get(country_code_or_name, country_code_or_name)


def get_usernames_by_country(country):
    """
    Returns a list of usernames for users belonging to the specified country.
    Accepts both full country names and ISO country codes.
    """
    normalized_country = normalize_country(country)
    print(f"Looking up users from country: {normalized_country}")

    username_list = []

    with current_app.app_context():
        users_from_country = User.query.filter_by(country=normalized_country).all()

        for user in users_from_country:
            username_list.append(user.username)

    return username_list



# === Text Cleaning and Comparison Utilities ===

def is_name_match(user_input, actual_name):
    """
    Compares two names using fuzzy ratio and soundex phonetic match.
    Returns True if names are similar enough to accept.
    """
    similarity = fuzz.ratio(user_input, actual_name)
    soundex_match = soundex(user_input) == soundex(actual_name)

    print(f"Comparing: '{user_input}' vs '{actual_name}'")
    print(f"Fuzzy ratio: {similarity}")
    print(f"Soundex codes: {soundex(user_input)} vs {soundex(actual_name)}")
    print(f"Soundex match: {soundex_match}")

    if similarity >= 90 or (similarity >= 80 and soundex_match):
        return True
    return False
      
  


def strip_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )


def clean_name(name, remove_spaces=True):
    """
    Cleans a name string:
    - Normalize multiple spaces
    - Removes periods and hyphens
    - Removes spaces if remove_spaces=True (for usernames, not manager names)
    """
    if name:
        name = re.sub(r'\s+', ' ', name).strip()
        cleaned_name = re.sub(r'[.,-]', '', name)
        if remove_spaces:
            cleaned_name = cleaned_name.replace(" ", "")
        return cleaned_name.lower()
    return None

def normalize_date_string(text):
    """
    Parses natural language date strings into 'YYYY-MM-DD' format.
    Returns None if parsing fails.
    """
    parsed_date = dateparser.parse(text)
    if parsed_date:
        return parsed_date.strftime("%Y-%m-%d")
    return None

def extract_username(text):
    """
    Extracts the username from phrases like:
    'My username is jsmith'
    'username is john.doe'
    'This is my username: jsmith'
    """
    if not text:
        return None

    # Normalize to lowercase for easier matching
    text = text.lower()

    # Common patterns we expect users to say
    patterns = [
        r'my username is\s+(.*)',
        r'username is\s+(.*)',
        r'this is my username\s*:\s*(.*)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            username = match.group(1)
            return username.strip()

    # If no pattern matched, fallback: assume entire text is the username
    return text.strip()
