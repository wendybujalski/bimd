from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired, Optional
from models import User

class SearchForm(FlaskForm):
    """Form for searching for a movie."""

    title = StringField('Search for a movie!', validators=[DataRequired()], render_kw={"placeholder": "Type the title of the movie here"})

class UserSignUpForm(FlaskForm):
    """Form for signing up a user."""

    username = StringField('Username', validators=[DataRequired(), Length(max=30)], render_kw={'maxlength': 30})
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=100)], render_kw={'maxlength': 100})
    password = PasswordField("Password", validators=[InputRequired(), EqualTo('password_confirm', message="Passwords do not match!"), Length(min=8, max=100)], render_kw={'minlength': 8, 'maxlength': 100})
    password_confirm = PasswordField("Confirm Password")

class UserLoginForm(FlaskForm):
    """Form for logging in as a user."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8, max=100)], render_kw={'minlength': 8, 'maxlength': 100})

class UserEditForm(FlaskForm):
    """Form for editing a user's info."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    old_password = PasswordField('Current Password', validators=[Length(min=8, max=100)], render_kw={'minlength': 8, 'maxlength': 100})
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8, max=100)], render_kw={'minlength': 8, 'maxlength': 100})

class UserRoleForm(FlaskForm):
    role = SelectField('Role', coerce=int)

class MovieCommentForm(FlaskForm):
    """Form for adding or editing a comment on a movie."""

    subject = StringField('Comment Title', validators=[Length(max=100)], render_kw={'maxlength': 100})
    text = TextAreaField('Comment Text')
    tags = SelectMultipleField('Tags', coerce=int)

class TagForm(FlaskForm):
    """Form for adding or editing a tag for the database. Moderators and Admins only."""

    name = StringField('Tag Name', validators=[DataRequired(), Length(max=100)], render_kw={'maxlength': 100})
    description = TextAreaField('Description')