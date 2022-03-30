from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db
from secrets import SECRET_KEY

DATABASE_NAME = "bimd"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route("/")
def index():
    """Display home page."""

    return render_template("index.html")