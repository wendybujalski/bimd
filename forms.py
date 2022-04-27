from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired
from models import User

class SearchForm(FlaskForm):
    """Form for searching for a movie."""

    title = StringField('Search for a movie!', validators=[DataRequired()], render_kw={"placeholder": "Type the title of the movie here"})

class UserSignUpForm(FlaskForm):
    """Form for signing up a user."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), EqualTo('password_confirm', message="Passwords do not match!"), Length(min=8, max=100)])
    password_confirm = PasswordField("Confirm Password")

class UserLoginForm(FlaskForm):
    """Form for logging in as a user."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])

class UserEditForm(FlaskForm):
    """Form for editing a user's info."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    old_password = PasswordField('Current Password', validators=[Length(min=8)])

class AddMovieCommentForm(FlaskForm):
    """Form for adding a comment to a movie."""

    # NOT DONE!

class EditMovieCommentForm(FlaskForm):
    """Form for editing a comment on a movie."""

    # NOT DONE!

class AddTagForm(FlaskForm):
    """Form for adding a tag to the database. Moderators and Admins only."""

    # NOT DONE!

class EditTagForm(FlaskForm):
    """Form for editing a tag in the database. Moderators and Admins only."""

    # NOT DONE!