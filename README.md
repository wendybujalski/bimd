# Bigory In Media Database

[Capstone Proposal](https://docs.google.com/document/d/1GIy4LwWKh6X36isgLwzILPHXZzgog_CfAB5AXcOfQzI/edit?usp=sharing)

My first full-stack capstone project for the Springboard Software Engineering Career Track.

---

### **Tools Used**

This app makes use of [The Movie Database API](https://developers.themoviedb.org/) for all of the movie information. The app requests data on movies searched by users and stores it in the local PostgerSQL database.

Styling was achieved using [Bootstrap](https://getbootstrap.com/).

The tag statistics charts are built using [Chart.js](https://www.chartjs.org/).

Other Tools Used -

- Flask
- SQL/PostgreSQL
- SQLAlchemy
- bcrypt
- WTForms

---

### **User Flow**

Without registering an account, users can search the database of movies and see the comments/tags left by other users.

To add content to the database, a user must register an account. New user accounts are given the role of user.

Once registered, a user can leave one comment per movie. The comment consists of a description of the content of the movie which the user considers bigoted as well as any number of tags.

All of the tags left on a movie by users are compiled into a graph on the movie's page.

Tags can be added, edited, and removed only by users with the role of admin or moderator. Roles can only be changed by admin users.

---

### **Running the App Locally (python3 and PostgreSQL required)**

Setting up the secrets file

1. You will need need an API key from [The Movie Database API](https://developers.themoviedb.org/). Sign up for an account there to get your API key.
2. Create a file named _secrets.py_ on the same level as _app.py_.
3. Add the following two variables to _secrets.py_
    * **TMDB_API_KEY** - set this to your [The Movie Database API](https://developers.themoviedb.org/) key.
    * **SECRET_KEY** - set this to a secret key of your choice.

Once you've added the secrets file, type the following into the Terminal in the root directory of the project -

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `createdb bimd`
5. `flask run`
