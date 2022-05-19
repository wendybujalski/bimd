import requests, os
from flask import Flask, render_template, redirect, session, g, flash, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from models import connect_db, db, bcrypt, Role, User, Tag, Movie, MovieComment, MovieCommentTag
from forms import SearchForm, UserEditForm, UserLoginForm, UserSignUpForm, MovieCommentForm, TagForm, UserRoleForm
try:
    from secrets import SECRET_KEY, TMDB_API_KEY
except: 
    SECRET_KEY = "no secrets file"
    TMDB_API_KEY = "api key not properly set"

API_BASE_URL = "https://api.themoviedb.org/3/"
API_POSTER_PATH = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
NO_POSTER_PATH = "./static/no-poster.png"
CURR_USER_KEY = "curr_user"
DATABASE_NAME = "bimd"

tmdb_api_key = os.environ.get("TMDB_API_KEY", TMDB_API_KEY)
database_uri = os.environ.get("DATABASE_URL", f'postgresql:///{DATABASE_NAME}')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SECRET_KEY)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
#toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

def debug_print(i):
    print("==========================================================================\n")
    print(i)
    print("\n==========================================================================")

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

def auth(permission=35):
    """Check if a user is logged in properly and has adequate permissions."""
    if not g.user:
        return False
    else:
        return authenticate(g.user.username, permission)

def authenticate(username, permission=35):
    """Check if the given user is logged in properly and has adequate permissions."""
    if not g.user:
        return False

    user = User.query.filter_by(username=username).one_or_none()

    if user != g.user or user.role.value > permission:
        return False
    
    return True

def auth_to_edit_tag(tag):
    """Check if the user is logged in and has adequate permissions to edit the given tag."""
    if not g.user:
        return False

    user = User.query.filter_by(username=g.user.username).one_or_none()

    if user != g.user:
        return False
    elif user.role == Role.admin or tag.created_by == user:
        return True
    else:
        return False

def auth_to_edit_comment(comment):
    """Check if the user is logged in and has adequate permissions to edit the given comment."""
    if not g.user:
        return False

    user = User.query.filter_by(username=g.user.username).one_or_none()

    if user != g.user:
        return False
    elif user.role == Role.admin or comment.user == user:
        return True
    else:
        return False

def auth_to_delete_comment(comment):
    """Check if the user is logged in and has adequate permissions to delete the given comment."""
    if not g.user:
        return False

    user = User.query.filter_by(username=g.user.username).one_or_none()

    if user != g.user:
        return False
    elif user.role.value < 11 or comment.user == user:
        return True
    else:
        return False

############################################################################################
#
# Main routes for home page, about, search, login, logout, and signup
#
############################################################################################

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

        except (InvalidRequestError, IntegrityError):
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

@app.route("/search")
def search():
    """Display search results."""

    query = request.args.get("q")
    page = int(request.args.get("page") or 1)

    if(not query):
        flash("You must enter a search query to view the search page.", "danger")
        return redirect("/")

    # Get the current page of search results.
    res = requests.get(
        f"{API_BASE_URL}search/movie",
        params={"api_key": tmdb_api_key, "query": query, "page": page}
    )
    data = res.json()
    results = data["results"]

    for m in results:
        # make release date object and prepare pretty string version for display
        relDateObj = Movie.convert_release_date_to_datetime(m)
        if relDateObj:
            m["release_date_str"] = relDateObj.strftime("%B %d, %Y")

        #placeholder image for poster if no image is present
        if (not "poster_path" in m) or (not m["poster_path"]):
            m["poster_path"] = NO_POSTER_PATH
        else:
            m["poster_path"] = API_POSTER_PATH + m["poster_path"]

        # check if this movie is in our database - if not, add the info we want to keep to it
        movie = Movie.query.get(m["id"])
        if movie == None:
            movie = Movie(id=m["id"], title=m["title"], poster_path=m["poster_path"], release_date=relDateObj, overview=m["overview"])

            db.session.add(movie)
            db.session.commit()

    return render_template("search.html", query=query, page=page, results=results, total_pages=data["total_pages"])

############################################################################################
#
# Routes to display a user's page, edit the user, and set their role
#
############################################################################################

@app.route("/u/<username>")
def user(username):
    """Display user account information for the given  user."""

    user = User.query.filter_by(username=username).first_or_404()
    comments = MovieComment.query.filter_by(user_id=user.id).all()

    debug_print(comments)

    return render_template("users/user.html", user=user, comments=comments)

@app.route("/u/<username>/edit", methods=["GET", "POST"])
def edit(username):
    """Edit your user account."""

    if not authenticate(username):
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

@app.route("/u/<username>/role", methods=["GET", "POST"])
def set_role(username):
    """Set the role for a user."""

    # Check if the user currently logged in is an admin.
    if not auth(0):
        flash("Access unauthorized.", "danger")
        return redirect(f"/u/{username}")
    
    user = User.query.filter_by(username=username).one_or_none()

    if not user:
        flash("That user does not exist.", "danger")
        return redirect("/")

    form = UserRoleForm(obj=user)
    form.role.choices = [(role.value, role.name) for role in Role]

    if form.validate_on_submit():
        try:
            user.role = Role(form.role.data)

            db.session.add(user)
            db.session.commit()
        except (InvalidRequestError, IntegrityError):
            flash("Error setting user role.", 'danger')
            db.session.rollback()
            return render_template("users/role.html", form=form, user=user)

        flash(f"{user.username} role updated successfully!", "success")
        return redirect(f"/u/{user.username}")
    else:
        return render_template("users/role.html", form=form, user=user)


############################################################################################
#
# Routes to display a movie, add/edit/delete comments on movies, and display one comment
#
############################################################################################

@app.route("/m/<int:id>")
def show_movie(id):
    """Page for an individual movie."""

    # First check to see if this movie is in our database.
    movie = Movie.query.get(id)

    # If it is not in our database, send a request to TMDb to get the info and put it in our database.
    if movie == None:
        res = requests.get(f"{API_BASE_URL}movie/{id}", params={"api_key": tmdb_api_key})
        m = res.json()
        relDateObj = Movie.convert_release_date_to_datetime(m)

        poster_path = NO_POSTER_PATH
        if "poster_path" in m and  m["poster_path"]:
            poster_path = API_POSTER_PATH + m["poster_path"]

        movie = Movie(id=m["id"], title=m["title"], poster_path=poster_path, release_date=relDateObj, overview=m["overview"])

        db.session.add(movie)
        db.session.commit()
    # Then the data is in our database and we can load it to the page below.

    # Also load the MovieComments and MovieCommentTags for this page to display as well.
    comments = MovieComment.query.filter(MovieComment.movie_id == id).all()

    # Remove comments from the list which come from banned or shadowbanned users
    comments = list(filter(lambda c: c.user.role.value < 30, comments))

    # If the user is logged in, check to see if they left a comment and load it as well.
    user_comment = None
    user = None
    if g.user:
        user_comment = MovieComment.query.filter_by(user_id=g.user.id, movie_id=id).one_or_none()
        user = g.user

    # Calculate tag stats for the page
    stats = {}
    tag_ids = {}
    for comment in comments:
        if comment.user.role.value < 30: # remove shadow banned and banned user comments from the stats
            for tag in comment.tags:
                if(tag.tag.active):
                    stats[tag.tag.name] = stats.get(tag.tag.name, 0) + 1 
                    tag_ids[tag.tag.name] = tag.tag.id
    stats = sorted(((v, k) for k, v in stats.items()), reverse=True)

    return render_template("movies/show.html", movie=movie, comments=comments, user_comment=user_comment, user=user, stats=stats, tag_ids=tag_ids)

@app.route("/m/<int:id>/add", methods=["GET", "POST"])
def add_comment(id):
    """Form for adding a comment to a movie."""

    if not auth():
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Prevent users from adding a second comment.
    existing_comment = MovieComment.query.filter_by(movie_id=id, user_id=g.user.id).one_or_none()
    if existing_comment:
        flash("You can only add one comment per movie.", "danger")
        return redirect(f"/m/{id}/c/{existing_comment.id}/edit")

    # Get the movie.
    movie = Movie.query.get(id)

    # Set up the form
    form = MovieCommentForm()
    form.tags.choices = [(t.id, t.name) for t in Tag.query.order_by('name')]

    if form.validate_on_submit():
        try:
            comment = MovieComment(
                movie_id = id,
                user_id = g.user.id,
                subject = form.subject.data,
                text = form.text.data
            )

            db.session.add(comment)
            db.session.commit()

            tags = []

            for tag in form.tags.data:
                tags.append(MovieCommentTag(
                    movie_comment_id=comment.id,
                    tag_id = tag
                ))
            db.session.add_all(tags)
            db.session.commit()

        except (InvalidRequestError, IntegrityError):
            flash("You can only add one comment per movie.", 'danger')
            return redirect(f'/m/{id}')

        flash("Comment Added!", 'success')
        return redirect(f'/m/{id}')
    else:
        return render_template("movies/add_comment.html", form=form, movie=movie)

@app.route("/m/<int:movie_id>/c/<int:comment_id>")
def view_comment(movie_id, comment_id):
    """Page to view one comment from a movie."""

    user = None
    if auth():
        user = g.user
    else:
        do_logout()

    # Get the movie.
    movie = Movie.query.get(movie_id)

    # Get the comment.
    comment = MovieComment.query.get(comment_id)
    
    # Determine if the comment belongs to the current user.
    your_comment = comment.user == user

    return render_template("movies/view_comment.html", movie=movie, c=comment, user=user, your_comment=your_comment)

@app.route("/m/<int:movie_id>/c/<int:comment_id>/edit", methods=["GET", "POST"])
def edit_comment(movie_id, comment_id):
    """Page to edit a comment on a movie."""

    # Get the comment.
    comment = MovieComment.query.get(comment_id)

    # Confirm the current user has permission to edit the comment.
    if not auth_to_edit_comment(comment):
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Set up the form
    form = MovieCommentForm(obj=comment)
    form.tags.choices = [(t.id, t.name) for t in Tag.query.order_by('name')]

    if form.validate_on_submit():
        try:
            comment.subject = form.subject.data
            comment.text = form.text.data

            db.session.add(comment)

            # Remove old tags before assigning the new ones
            old_tags = MovieCommentTag.query.filter_by(movie_comment_id=comment.id).all()
            for t in old_tags:
                db.session.delete(t)
            db.session.commit()

            tags = []

            for tag in form.tags.data:
                tags.append(MovieCommentTag(
                    movie_comment_id=comment.id,
                    tag_id = tag
                ))
            db.session.add_all(tags)
            db.session.commit()

        except (InvalidRequestError, IntegrityError):
            flash("Error editing comment.", 'danger')
            return redirect(f'/m/{movie_id}')

        flash("Comment Updated!", 'success')
        return redirect(f'/m/{movie_id}')
    else:
        # Get the movie.
        movie = Movie.query.get(movie_id)
        
        # Set the form defaults for the tags
        form.tags.data = [tag.tag.id for tag in comment.tags]

        return render_template("movies/edit_comment.html", form=form, movie=movie)

@app.route("/m/<int:movie_id>/c/<int:comment_id>/delete", methods=["POST"])
def delete_comment(movie_id, comment_id):
    """Page to delete a comment on a movie."""

    # Get the comment.
    comment = MovieComment.query.get(comment_id)

    # Confirm the current user has permission to delete the comment.
    if not auth_to_delete_comment(comment):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    # Delete the comment.
    try:
        db.session.delete(comment)
        db.session.commit()

    except (InvalidRequestError,IntegrityError) :
        flash("Comment could not be deleted", 'danger')
        return redirect(f'/m/{movie_id}/c/{comment_id}')
    
    flash("Comment deleted!", 'success')
    return redirect(f'/m/{movie_id}')

############################################################################################
#
# Routes related to tags which can only be accessed by mods and admins
#
############################################################################################

@app.route("/tags")
def tags():
    """Page to view all tags in the database."""

    if not auth(10):
        flash("Access unauthorized.", "danger")
        return redirect("/")

    tags = Tag.query.all()
    hidden = [tag for tag in tags if not tag.active]
    tags = [tag for tag in tags if tag not in hidden]
    
    return render_template("tags/list.html", tags=tags, hidden=hidden, user=g.user)

@app.route("/tags/new", methods=["GET", "POST"])
def new_tag():
    """Form to add a new tag to the database."""

    if not auth(10):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = TagForm()

    if form.validate_on_submit():
        try:
            tag = Tag(
                name=form.name.data,
                description=form.description.data,
                created_by_id=g.user.id,
                active=True
            )
            db.session.add(tag)
            db.session.commit()

        except (InvalidRequestError, IntegrityError):
            flash("Tag name already taken", 'danger')
            return render_template('tags/new.html', form=form)

        flash("Tag created!", 'success')
        return redirect("/tags")
    else:
        return render_template("tags/new.html", form=form)

@app.route("/tags/<int:id>")
def see_tag(id):
    """Route to see a single tag's page."""

    tag = Tag.query.get(id)

    return render_template("tags/show.html", tag=tag, user=g.user)

@app.route("/tags/<int:id>/edit", methods=["GET", "POST"])
def edit_tag(id):
    """Form to edit an existing tag in the database."""

    if not auth(10):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    tag = Tag.query.get(id)

    if not auth_to_edit_tag(tag):
        flash("You do not have permission to edit that tag.", "danger")
        return redirect("/")

    form = TagForm(obj=tag)

    if form.validate_on_submit():
        try:
            tag.name = form.name.data
            tag.description = form.description.data
            
            db.session.add(tag)
            db.session.commit()

        except (InvalidRequestError, IntegrityError):
            flash("Tag name already taken", 'danger')
            return render_template('/tags/edit.html', form=form)

        flash("Tag updated!", 'success')
        return redirect("/tags")
    else:
        return render_template("tags/edit.html", form=form)

@app.route("/tags/<int:id>/hide", methods=["POST"])
def hide_tag(id):
    """Post route for hiding a tag."""

    if not auth(10):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    tag = Tag.query.get(id)

    if not auth_to_edit_tag(tag):
        flash("You do not have permission to edit that tag.", "danger")
        return redirect("/")
    
    try:
        tag.active = False

        db.session.add(tag)
        db.session.commit()

    except (InvalidRequestError, IntegrityError):
        flash("Tag could not be updated", 'danger')
        return render_template('/tags')
    
    flash("Tag updated!", 'success')
    return redirect("/tags")

@app.route("/tags/<int:id>/show", methods=["POST"])
def show_tag(id):
    """Post route for showing a tag."""

    if not auth(10):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    tag = Tag.query.get(id)

    if not auth_to_edit_tag(tag):
        flash("You do not have permission to edit that tag.", "danger")
        return redirect("/")
    
    try:
        tag.active = True

        db.session.add(tag)
        db.session.commit()

    except (InvalidRequestError, IntegrityError):
        flash("Tag could not be updated", 'danger')
        return render_template('/tags')
    
    flash("Tag updated!", 'success')
    return redirect("/tags")

@app.route("/tags/<int:id>/delete", methods=["POST"])
def delete_tag(id):
    """Post route for deleting a tag."""

    if not auth(10):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    tag = Tag.query.get(id)

    if not auth_to_edit_tag(tag):
        flash("You do not have permission to edit that tag.", "danger")
        return redirect("/")
    
    try:
        db.session.delete(tag)
        db.session.commit()

    except (InvalidRequestError, IntegrityError):
        flash("Tag could not be deleted", 'danger')
        return render_template('/tags')
    
    flash("Tag deleted!", 'success')
    return redirect("/tags")