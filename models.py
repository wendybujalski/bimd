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

    __tablename__ = "user"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default="user")
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

class Tag(db.Model):
    """Model for the Tag table"""

    __tablename__ = "tag"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text())

    user = db.relationship("User")

class MovieComment(db.Model):
    """Model for the MovieComment table"""
    """Each user can leave one MovieComment on each Movie"""

    __tablename__ = "movie_comment"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
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