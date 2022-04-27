"""Models for project"""

from enum import Enum
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Role(Enum):
    admin = 0
    mod = 10
    user = 20
    shadow_ban = 30
    full_ban = 40

role_strings = {
    Role.admin: "Admin",
    Role.mod: "Moderator",
    Role.user: "User",
    Role.shadow_ban: "User",
    Role.full_ban: "Banned"
}

def connect_db(app):
    db.app = app
    db.init_app(app)

class Movie(db.Model):
    """Model for the Movie table"""

    __tablename__ = "movie"

    id = db.Column( db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)


class User(db.Model):
    """Model for the User table"""

    __tablename__ = "users"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default="user")
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    @property
    def role_string(self):
        """Returns a string representing the user's role."""
        return role_strings[self.role]

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            created=datetime.utcnow(),
            last_login=datetime.utcnow(),
            )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with username and password."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Tag(db.Model):
    """Model for the Tag table"""

    __tablename__ = "tag"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text())

    user = db.relationship("User")

class MovieComment(db.Model):
    """Model for the MovieComment table"""
    """Each user can leave one MovieComment on each Movie"""

    __tablename__ = "movie_comment"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(100))
    text = db.Column(db.Text())
    rating = db.Column(db.Integer) # may or may not implement

class MovieCommentTag(db.Model):
    """Model for the MovieCommentTag table"""
    """Each MovieComment can have multiple MovieCommentTags associated with it"""

    __tablename__ = "movie_comment_tag"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    movie_comment_id = db.Column(db.Integer, db.ForeignKey('movie_comment.id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), nullable=False)