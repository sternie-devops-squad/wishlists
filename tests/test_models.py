"""
Test cases for Wishlist Model

"""
import logging
import unittest
import os
from service import app, status
from service.models import Wishlist, Item, DataValidationError, db
from tests.factories import WishlistFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/wishlists"

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
        """ Creates an wishlist from a Factory """
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name, 
            user_id=fake_wishlist.user_id, 
            created_date=fake_wishlist.created_date,
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
            price=fake_item.price,
            in_stock=fake_item.in_stock,
            purchased=fake_item.purchased
        )
        self.assertTrue(item != None)
        self.assertEqual(item.id, None)
        return item

######################################################################
#  T E S T   C A S E S
######################################################################

    def test_create_an_wishlist(self):
        """ Create a Wishlist and assert that it exists """
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name, 
            user_id=fake_wishlist.user_id, 
            created_date=fake_wishlist.created_date 
        )
        self.assertTrue(wishlist != None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.user_id, fake_wishlist.user_id)
        self.assertEqual(wishlist.created_date, fake_wishlist.created_date)

    def test_add_a_wishlist(self):
        """ Create an wishlist and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = self._create_wishlist()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    def test_list_all_wishlists(self):
        """ List all Wishlists in the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        for _ in range(5):
            wishlist = self._create_wishlist()
            wishlist.create()
        # Assert that there are not 5 wishlists in the database
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 5)

    def test_read_a_wishlist(self):
        """ Read a wishlist """
        wishlist = self._create_wishlist()
        wishlist.create()

        # Read it back
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.id, wishlist.id)
        self.assertEqual(found_wishlist.name, wishlist.name)
        self.assertEqual(found_wishlist.user_id, wishlist.user_id)
        self.assertEqual(found_wishlist.created_date, wishlist.created_date)
    
    def test_update_a_wishlist(self):
        """ Update (Edit) a wishlist """
        wishlist = self._create_wishlist()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        wishlist.name = "pets"
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.name, "pets")
    
    def test_serialize_an_wishlist(self):
        """ Serialize an wishlist """
        item = self._create_item()
        wishlist = self._create_wishlist(items=[item])
        serial_wishlist = wishlist.serialize()
        self.assertEqual(serial_wishlist['id'], wishlist.id)
        self.assertEqual(serial_wishlist['name'], wishlist.name)
        self.assertEqual(serial_wishlist['user_id'], wishlist.user_id)
        self.assertEqual(serial_wishlist['created_date'], str(wishlist.created_date))
        self.assertEqual(len(serial_wishlist['items']), 1)
        items = serial_wishlist['items']
        self.assertEqual(items[0]['id'], item.id)
        self.assertEqual(items[0]['wishlist_id'], item.wishlist_id)
        self.assertEqual(items[0]['name'], item.name)
        self.assertEqual(items[0]['category'], item.category)
        self.assertEqual(items[0]['price'], item.price)
        self.assertEqual(items[0]['in_stock'], item.in_stock)
        self.assertEqual(items[0]['purchased'], item.purchased)

    def test_deserialize_an_wishlist(self):
        """ Deserialize an wishlist """
        item = self._create_item()
        wishlist = self._create_wishlist(items=[item])
        serial_wishlist = wishlist.serialize()
        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.id, wishlist.id)
        self.assertEqual(new_wishlist.name, wishlist.name)
        self.assertEqual(new_wishlist.user_id, wishlist.user_id)
        self.assertEqual(new_wishlist.created_date, wishlist.created_date)

    def test_deserialize_with_key_error(self):
        """ Deserialize an wishlist with a KeyError """
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_type_error(self):
        """ Deserialize an wishlist with a TypeError """
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_deserialize_item_key_error(self):
        """ Deserialize an item with a KeyError """
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """ Deserialize an item with a TypeError """
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_add_wishlist_item(self):
        """ Create an wishlist with an item and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = self._create_wishlist()
        item = self._create_item()
        wishlist.items.append(item)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.items[0].name, item.name)

        item2 = self._create_item()
        wishlist.items.append(item2)
        wishlist.update()

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(wishlist.items), 2)
        self.assertEqual(wishlist.items[1].name, item2.name)