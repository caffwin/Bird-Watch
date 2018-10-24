import unittest

from server import app
from model import db, example_data, connect_to_db


class birdwatchTests(unittest.TestCase):
    """ Tests for Bird Watch web app """

    def setUp(self):
    self.client = app.test_client()
    app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get('/')
        self.assertIn(b"Welcome to the bird watcc!", result.data)


    def test_not_logged_in(self):

        result = self.client.get("/")
        # Add a test to show prompt for login when no session['user_id'] 
        self.assertIn(b"Please log in", result.data)

    def test_logged_in(self):
        result = self.client.post("/login",
                                  data={'fname': "Jane",
                                        'lname': "Hacks",
                                        "email": "jhacks@gmail.com"},
                                  follow_redirects=True)
        # Login credentials are true, entry from dummy data

        self.assertIn(b"yo uare logged in!", result.data) # we want to see this
        self.assertNotIn(b"Please log in", result.data) # we don't want to see this


    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_my_page(self):
        """ Tests to see if certain strings are in my_page """
        result = self.client.get("/my_page")
        self.assertIn(b"<td>First Name:</td>", result.data)
        self.assertIn(b"<td>Favorites</td>", result.data)

if __name__ == "__main__":
    unittest.main()