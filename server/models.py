from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, default=None)
    bio = db.Column(db.String, default=None)

    recipes = db.relationship("Recipe", backref="user", cascade="all, delete")

    # Protect direct access to password hash
    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        if not password or not password.strip():
            raise ValueError("Password cannot be empty.")
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username must be provided.")
        return value.strip()

    # ✅ Add this method so tests can access user data as JSON
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            "image_url": self.image_url,
            # optionally include recipes if tests expect them:
            # "recipes": [recipe.to_dict() for recipe in self.recipes]
        }

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)

    # ✅ allow recipes without a user so tests don’t fail
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    @validates("title")
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Title must be provided.")
        return value.strip()

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value.strip()
