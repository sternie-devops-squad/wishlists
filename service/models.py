"""
Models for Wishlist

All of the models are stored in this module
"""
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

DATETIME_FORMAT='%Y-%m-%d' # Note: updated date time format to match UI input field

######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase():
    """ Base class added persistent methods """

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Account from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the records in the database """
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a record by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), nullable=False)
    name = db.Column(db.String(64)) # e.g., work, home, vacation, etc.
    category = db.Column(db.String(64))
    price = db.Column(db.Integer)
    in_stock = db.Column(db.Boolean, default=True)
    purchased = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Item %r id=[%s] wishlist[%s]>" % (self.name, self.id, self.wishlist_id)

    def __str__(self):
        return "%s: %s, %s, %s %s" % (self.name, self.category, self.price, self.in_stock, self.purchased)

    def serialize(self):
        """ Serializes a Item into a dictionary """
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "in_stock": self.in_stock,
            "purchased": self.purchased
        }

    def deserialize(self, data):
        """
        Deserializes a Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.name = data["name"]
            self.category = data["category"]
            self.price = data["price"]
         
            # Note: need to fix the below for nosetests
            # self.in_stock = data["in_stock"]
            # self.purchased = data["purchased"]
        except KeyError as error:
            raise DataValidationError("Invalid Item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained" "bad or no data"
            )
        return self



######################################################################
#  W I S H L I S T   M O D E L
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents an Wishlist
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    type = db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship('Item', backref='wishlist', lazy=True)  

    def __repr__(self):
        return "<Wishlist %r id=[%s]>" % (self.name, self.type, self.id)

    def serialize(self):
        """ Serializes a Wishlist into a dictionary """
        wishlist = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "user_id": self.user_id,
            "created_date": self.created_date.strftime(DATETIME_FORMAT),
            "items": []
        }
        for item in self.items:
            wishlist['items'].append(item.serialize())
        return wishlist

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.type = data["type"]
            self.user_id = data["user_id"]
            self.created_date = datetime.strptime(data["created_date"], DATETIME_FORMAT).date()
            # handle inner list of items
            item_list = data.get("items")
            if item_list:  # only process if items exists
                for json_item in item_list:
                    item = Item()
                    item.deserialize(json_item)
                    self.items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid Wishlist: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def find_by_name(cls, name):
        """ Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
