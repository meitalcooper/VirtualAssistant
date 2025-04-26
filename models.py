"""
Database model definitions for the Voice Assistant application.
Contains the User model which defines the structure of our user database table.
Each user has attributes like username, name, manager, country, and password hash
that are essential for the SSO troubleshooting system.
"""
from app import db
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional



class User(db.Model):
    __tablename__ = 'users'

    uid: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    manager: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False, index=True)
    hire_date: Mapped[date] = mapped_column(nullable=False)
    password_hashed: Mapped[str] = mapped_column(nullable=True, default=None)
    email: Mapped[str] = mapped_column(nullable=True, )



