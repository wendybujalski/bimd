import requests
from datetime import datetime
from flask import Flask, render_template, redirect, session, g, flash, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from models import connect_db, db, bcrypt, User
from forms import SearchForm, UserEditForm, UserLoginForm, UserSignUpForm
from secrets import SECRET_KEY, TMDB_API_KEY

API_BASE_URL = "https://api.themoviedb.org/3/"
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
        return redirect( url_for("search", q=form.title.data) )
    else:
        return render_template("index.html", form=form)

@app.route("/about")
def about():
    """Display the about page."""

    return render_template("about.html")

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

@app.route("/u/<username>/edit", methods=["GET", "POST"])
def edit(username):
    """Edit your user account."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.filter_by(username=username).first_or_404()

    if user != g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserEditForm(obj=g.user) # put the user's object here to prefill the form

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.old_password.data)

        if user:
            try:
                user.username = form.username.data
                user.email = form.email.data

                new_password = form.new_password.data
                if(len(new_password) > 7):
                    hashed_pwd = bcrypt.generate_password_hash(new_password).decode('UTF-8')
                    user.password = hashed_pwd

                db.session.add(user)
                db.session.commit()
            except (InvalidRequestError, IntegrityError):
                flash("Username or email already taken", 'danger')
                db.session.rollback()
                return render_template("users/edituser.html", form=form)

            do_login(user)
            flash(f"{user.username} edited successfully!", "success")
            return redirect(f"/u/{user.username}")
        else:
            flash("Invalid password, please try again.", 'danger')
            return render_template("users/edituser.html", form=form)
    else:
        return render_template("users/edituser.html", form=form)

@app.route("/m/<int:id>")
def show_movie(id):
    """Page for an individual movie."""

    # NOT DONE YET!
    # First check to see if this movie is in our database.
    # If it is not in our database, send a request to TMDb to get the info and put it in our database.
    # Then the data is in our database and we can load it to the page.
    # Also load the MovieComments and MovieCommentTags for this page to display as well.
    # Each MovieComment and MovieCommentTag should show with a link to the user profile to the person who posted it.
    # MovieComments and their tags from banned or shadowbanned users should not show.

    return render_template("movies/show.html")

@app.route("/search")
def search():
    """Display search results."""

    query = request.args.get("q")
    page = request.args.get("page") or "1"

    res = requests.get(
        f"{API_BASE_URL}search/movie",
        params={"api_key": TMDB_API_KEY, "query": query, "page": page}
    )
    data = res.json()["results"]
    for m in data:
        # make release date pretty
        if "release_date" in m and m["release_date"]:
            m["release_date"] = datetime.strptime(m["release_date"], "%Y-%m-%d").strftime("%B %d, %Y")

    # Before returning the results, we should dump data from the API into our database!
    # NOT DONE!

    return render_template("search.html", query=query, page=page, results=data)

# Additional routes and stuff to implement -

# Add comment and tags form for a particular movie. Should not allow banned users from submitting anything.
# A page that shows just a single MovieComment
# Add tag form which only mods and admins can access.
# Edit tag form which only mods and admins can access.
# Display each user's MovieComments on their user profile
# Ability to edit or delete a MovieComment
# Users should be able to edit/delete their own MovieComment or an admin can edit/delte or a mod can delete

# ANYTHING ELSE?