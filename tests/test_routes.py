"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from . import status  # HTTP Status Codes
from tests.factories import WishlistFactory, ItemFactory
from service import status  # HTTP Status Codes
from service.models import Wishlist, db
from service.routes import app, init_db

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/wishlists"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()


    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        pass

    #######################################################################
    #  H E L P E R   M E T H O D S
    #######################################################################

    def _create_wishlists(self, count):
        """ Factory method to create wishlists in bulk """
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.app.post(
                "/wishlists", json=wishlists.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Wishlist"
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists        


    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    def test_create_wishlist(self):
        """ Create a new Wishlist """
        test_wishlist = WishlistFactory()
        logging.debug(test_wishlist)
        resp = self.app.post(
            BASE_URL, json=test_wishlist.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

         # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], test_wishlist.name, "Names do not match")
        self.assertEqual(
            new_wishlist["user_id"], test_wishlist.user_id, "User Id's do not match"
        )
        self.assertEqual(
            new_wishlist["date_created"], test_wishlist.date_created, "Created Dates does not match"
        )