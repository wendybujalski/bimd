from flask import Flask, render_template, redirect, session, g, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from models import connect_db, db, User
from forms import SearchForm, UserEditForm, UserLoginForm, UserSignUpForm
from secrets import SECRET_KEY

CURR_USER_KEY = "curr_user"
DATABASE_NAME = "bimd"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
#toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.before_request
def add_user_to_g():
    """Before each request, add the current user to the global object if they are stored in the session"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route("/", methods=["GET", "POST"])
def index():
    """Display home page."""

    form = SearchForm()

    if form.validate_on_submit():
        # NOT DONE YET!

        return redirect("/search")
    else:
        return render_template("index.html", form=form)

@app.route("/about")
def about():
    """Display the about page."""

    return render_template("about.html")

@app.route("/search")
def search():
    """Display search results."""

    # NOT DONE YET!

    return render_template("search.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Sign up for a new account."""

    form = UserSignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username or email already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")
    else:
        return render_template("users/signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log into an existing account."""

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials. Please try again.", 'danger')

    return render_template("users/login.html", form=form)

@app.route("/logout")
def logout():
    """Handle logout of user."""

    user = User.query.get(session[CURR_USER_KEY])
    msg = f"Goodbye {user.username}!"

    do_logout()

    flash(msg, "success")

    return redirect("/")

@app.route("/u/<username>")
def user(username):
    """Display user account information for the given  user."""

    user = User.query.filter_by(username=username).first_or_404()

    return render_template("users/user.html", user=user)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    """Edit your user account."""

    # NOT DONE YET, SHOULD VALIDATE USER LOGGED IN

    form = UserEditForm() # put the user's object here to prefill the form

    if form.validate_on_submit():
        # NOT DONE YET!

        return redirect("/")
    else:
        return render_template("users/edituser.html", form=form)

