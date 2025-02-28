"""
Main Flask application configuration and initialization.
Sets up SQLAlchemy database connection, configures Flask-Migrate for database migrations,
and initializes Bcrypt for password hashing. This file serves as the core setup
for the Voice Assistant application.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_bcrypt import Bcrypt




# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
  pass

# Initialize database and bcrypt
db = SQLAlchemy(model_class=Base)
bcrypt = Bcrypt()

def create_app():
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./ivr_users.db" # Set up the database location

  # Initialize the database with the app
  db.init_app(app)
  bcrypt.init_app(app)

  # Register the routes from twilio_routes.py
  from twilio_routes import register_twilio_routes
  register_twilio_routes(app)
  
  # Set up database migrations
  migrate = Migrate(app, db)

  import models

  return app