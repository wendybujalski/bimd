import os
from unittest import TestCase
from app import app, DATABASE_NAME
from models import db, User, Movie, Tag, MovieComment, MovieCommentTag

os.environ['DATABASE_URL'] = f'postgresql:///{DATABASE_NAME}_test'
app.config['WTF_CSRF_ENABLED'] = False
db.create_all()

TEST_ID_1 = 666

class FlaskRouteTests(TestCase):
    """Tests for the Flask routes."""

    def set_up(self):
        """Code to run before each test."""

        # Set up the test client

        db.drop_all()
        db.create_all() 
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

        # Set up the test data

        test_user = User.signup("test_user", "test_user@test.com", "test_password")
        test_user_id = TEST_ID_1
        test_user.id = test_user_id
        db.session.commit()

        test_comment = MovieComment(
                movie_id = 2, # Movie Title - "Ariel"
                user_id = test_user_id,
                subject = "Test Comment",
                text = "Test comment text.")
        test_comment_id = TEST_ID_1
        test_comment.id = test_comment_id
        db.session.commit()
        
        
    
    def test_page_index(self):
        """Test to confirm that the index displays properly."""

        with self.client:
            res = self.client.get("/")

            self.assertEqual(res.status_code, 200) # make sure it responds with an ok status code
            self.assertIn(b'<h1 id="main-title">Welcome to the Bigotry In Media Database!</h1>', res.data) # it should have the title
            self.assertIn(b'<button type="submit" class="btn btn-primary">Search The Database</button>', res.data) # it should have the button to search
    
    def test_page_about(self):
        """Test to confirm that the about page displays properly."""

        with self.client:
            res = self.client.get("/about")

            self.assertEqual(res.status_code, 200) # make sure it responds with an ok status code
            self.assertIn(b'<h1 id="main-title">About the Bigotry In Media Database</h1>', res.data) # it should have the title
            self.assertIn(b'<img src="./static/tmdb.svg" class="img-fluid">', res.data) # it should have the TMDB logo
    
    def test_page_signup(self):
        """Test to confirm that the sign up page displays properly."""

        with self.client:
            res = self.client.get("/signup")

            self.assertEqual(res.status_code, 200) # make sure it responds with an ok status code
            self.assertIn(b'<h2>Sign Up</h2>', res.data) # it should have the title
            self.assertIn(b'<button class="btn btn-primary btn-block btn-lg">Sign Up</button>', res.data) # it should have the button to submit the form
    
    def test_page_login(self):
        """Test to confirm that the log in page displays properly."""

        with self.client:
            res = self.client.get("/login")

            self.assertEqual(res.status_code, 200) # make sure it responds with an ok status code
            self.assertIn(b'<h2>Log In</h2>', res.data) # it should have the title
            self.assertIn(b'<button class="btn btn-primary btn-block btn-lg">Log in</button>', res.data) # it should have the button to submit the form

    def test_signup(self):
        """Test signing a user up for an account."""
        pass
        # TODO
    
    def test_login(self):
        """Test logging a user into their account."""
        pass
        # TODO
    
    def test_logout(self):
        """Test logging a user out of their account."""
        pass
        # TODO
    
    def test_search(self):
        """Test a search of the database."""
        pass
        # TODO