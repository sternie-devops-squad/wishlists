"""
Test cases for YourResourceModel Model

"""
import logging
import unittest
import os
from service import app
from service.models import Wishlist, Item, DataValidationError, db
from tests.factories import WishlistFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlist(unittest.TestCase):
    """ Test Cases for Wishlist Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Wishlist.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_wishlist(self, items=[]):
        """ Creates a wishlist from a Factory """
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name, 
            user_id=fake_wishlist.user_id, 
            date_created=fake_wishlist.date_created, 
            items=items
        )
        self.assertTrue(wishlist != None)
        self.assertEqual(wishlist.id, None)
        return wishlist

    def _create_item(self):
        """ Creates fake items from factory """
        fake_item = ItemFactory()
        item = Item(
            name=fake_item.name,
            category=fake_item.category,
            in_stock=fake_item.in_stock,
            price=fake_item.price,
            purchased=fake_item.purchased
        )
        self.assertTrue(item != None)
        self.assertEqual(item.id, None)
        return item
    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """ Create a Wishlist and assert that it exists """
        fake_account = WishlistFactory()
        wishlist = Wishlist(
            name=fake_account.name, 
            user_id=fake_account.user_id, 
            date_created=fake_account.date_created, 
        )
        self.assertTrue(wishlist != None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_account.name)
        self.assertEqual(wishlist.user_id, fake_account.user_id)
        self.assertEqual(wishlist.date_created, fake_account.date_created)