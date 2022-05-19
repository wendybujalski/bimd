# Bigory In Media Database

[Capstone Proposal](https://docs.google.com/document/d/1GIy4LwWKh6X36isgLwzILPHXZzgog_CfAB5AXcOfQzI/edit?usp=sharing)

My first full-stack capstone project for the Springboard Software Engineering Career Track.

This app is now [deployed here!](LINK).

Live Link: LINK

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