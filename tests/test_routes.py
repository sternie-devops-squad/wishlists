"""
<your resource name> API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from tests.factories import WishlistFactory, ItemFactory
from service import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/wishlists"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistService(TestCase):
    """ Wishlist Service Tests """

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
        """ Runs once before test suite """
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ Runs once after each test case """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_wishlists(self, count):
        """ Factory method to create wishlists in bulk """
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.app.post(
                BASE_URL, json=wishlist.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Wishlist"
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists

######################################################################
#  W I S H L I S T   T E S T   C A S E S
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_wishlist_list(self):
        """ Get a list of Wishlists """
        self._create_wishlists(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_wishlist_by_name(self):
        """ Get a Wishlist by Name """
        wishlists = self._create_wishlists(3)
        resp = self.app.get(
            BASE_URL, 
            query_string=f"name={wishlists[1].name}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], wishlists[1].name)

    def test_get_wishlist(self):
        """ Get a single Wishlist """
        # get the id of an wishlist
        wishlist = self._create_wishlists(1)[0]
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}", 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], wishlist.name)

    def test_get_wishlist_not_found(self):
        """Get a Wishlist that is not found"""
        resp = self.app.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist(self):
        """ Create a new Wishlist """
        wishlist = WishlistFactory()
        resp = self.app.post(
            BASE_URL, 
            json=wishlist.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        
        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(new_wishlist["type"], wishlist.type, "Type does not match")
        self.assertEqual(new_wishlist["items"], wishlist.items, "Item does not match")
        self.assertEqual(new_wishlist["user_id"], wishlist.user_id, "user_id does not match")
        self.assertEqual(new_wishlist["created_date"], str(wishlist.created_date), "Created Date does not match")

        # Check that the location header was correct by getting it
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(new_wishlist["type"], wishlist.type, "Type does not match")
        self.assertEqual(new_wishlist["items"], wishlist.items, "Item does not match")
        self.assertEqual(new_wishlist["user_id"], wishlist.user_id, "user_id does not match")
        self.assertEqual(new_wishlist["created_date"], str(wishlist.created_date), "Created Date does not match")
    
    def test_update_wishlist(self):
        """ Update (Edit) an existing Wishlist """
        # create a wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.app.post(
            BASE_URL, 
            json=test_wishlist.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the wishlist
        new_wishlist = resp.get_json()
        new_wishlist["name"] = "Pets"
        new_wishlist_id = new_wishlist["id"]
        resp = self.app.put(
            f"{BASE_URL}/{new_wishlist_id}",
            json=new_wishlist,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "Pets")
    
    def test_update_wishlist_not_found(self):
        """Update a Wishlist that does not exist"""
        new_wishlist = WishlistFactory()
        resp = self.app.put(
            f"{BASE_URL}/0",
            json=new_wishlist.serialize(),
            content_type="application/json"
         )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist(self):
        """ Delete an Wishlist """
        # get the id of an wishlist
        wishlist = self._create_wishlists(1)[0]
        resp = self.app.delete(
            f"{BASE_URL}/{wishlist.id}", 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # Error handler testing code below based on the Service_Accounts code example
    def test_bad_request(self):
        """ Send wrong media type """
        wishlist = WishlistFactory()
        resp = self.app.post(
            BASE_URL, 
            json={"name": "not enough data"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unsupported_media_type(self):
        """ Send wrong media type """
        wishlist = WishlistFactory()
        resp = self.app.post(
            BASE_URL, 
            json=wishlist.serialize(), 
            content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """ Make an illegal method call """
        resp = self.app.put(
            BASE_URL, 
            json={"not": "today"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

######################################################################
#  I T E M  T E S T   C A S E S
######################################################################

    def test_get_item_list(self):
        """ Get a list of Items """
        # add two items to wishlist
        wishlist = self._create_wishlists(1)[0]
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", 
            json=item_list[0].serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item_list[1].serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}/items", 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_add_item(self):
        """ Add an item to a wishlist """
        wishlist = self._create_wishlists(1)[0]
        item = ItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["category"], item.category)
        self.assertEqual(data["price"], item.price)
        # self.assertEqual(data["in_stock"], item.in_stock)
        # self.assertEqual(data["purchased"], item.purchased)

    def test_get_item(self):
        """ Get an item from an wishlist """
        # create a known item
        wishlist = self._create_wishlists(1)[0]
        item = ItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["category"], item.category)
        self.assertEqual(data["price"], item.price)
        # self.assertEqual(data["in_stock"], item.in_stock)
        # self.assertEqual(data["purchased"], item.purchased)

    def test_update_item(self):
        """ Update an item on an wishlist """
        # create a known item
        wishlist = self._create_wishlists(1)[0]
        item = ItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", 
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.app.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=data, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], "XXXX")

    def test_delete_item(self):
        """ Delete an Item """
        wishlist = self._create_wishlists(1)[0]
        item = ItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.app.delete(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)       


######################################################################
# T E S T   A C T I O N S
######################################################################

    def test_purchase_a_item(self):
        """Purchase an Item"""
        wishlist = self._create_wishlists(1)[0]
        item = ItemFactory()
        item.in_stock = True
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_data = resp.get_json()
        item_id = item_data["id"]
        logging.info(f"Created Item with id {item_id} = {item_data}")

        # Request to purchase a Item
        resp = self.app.put(f"{BASE_URL}/{wishlist.id}/items/{item_id}/purchase")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Retrieve the Item and make sue it is purchased
        resp = self.app.get(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item_data = resp.get_json()
        self.assertEqual(item_data["id"], item_id)
        self.assertEqual(item_data["purchased"], True)

# Note: FIX ME PLEASE!
    # def test_purchase_not_available(self):
    #     """Purchase a Item that is not in stock"""
    #     wishlist = self._create_wishlists(1)[0]

    #     item = ItemFactory()
    #     item.in_stock = False

    #     resp = self.app.post(
    #         f"{BASE_URL}/{wishlist.id}/items",
    #         json=item.serialize(), 
    #         content_type="application/json"
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     item_data = resp.get_json()
    #     item_id = item_data["id"]
    #     item_is = item_data["in_stock"]
    #     logging.info(f"Created Item with id {item_id} = {item_data}")
    #     logging.info(f"Item in stock {item_is}")
        
    #     # Request to purchase a Item should fail
    #     resp = self.app.put(f"{BASE_URL}/{wishlist.id}/items/{item_id}/purchase")
    #     self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_purchase_a_item_not_found(self):
        """Purchase a Item not found"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.app.put(f"{BASE_URL}/{wishlist.id}/items/{0}/purchase")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    