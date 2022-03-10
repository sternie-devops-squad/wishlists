"""
Models for Account

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

DATETIME_FORMAT='%Y-%m-%d %H:%M:%S.%f'

######################################################################
#  P E R S I S T E N T   B A S E   M O D E L (no touchy)
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

    def save(self):
        """
        Updates a Account to the database
        """
        logger.info("Saving %s", self.name)
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

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a record by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents a wishlist item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., work, home, vacation, etc.
    category = db.Column(db.String(64), nullable=False)
    in_stock = db.Column(db.Boolean(), nullable=False, default=False)
    price = db.Column(db.Integer)
    purchased = db.Column(db.Boolean(), default=False)


    def __repr__(self):
        return "<Item %r id=[%s] wishlist[%s]>" % (self.name, self.id, self.wishlist_id)

    def __str__(self):
        return "%s: %s, %s, %s %s" % (self.name, self.category, self.in_stock, self.price)

    def serialize(self):
        """ Serializes an Item into a dictionary """
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "name": self.name,
            "category": self.category,
            "in_stock": self.in_stock,
            "price": self.price,
            "purchased": self.postalcode
        }

    def deserialize(self, data):
        """
        Deserializes an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.name = data["name"]
            self.category = data["category"]
            self.in_stock = data["in_stock"]
            self.price = data["price"]
            self.purchased = data["purchased"]
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
    Class that represents a Wishlist
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship('Item', backref='wishlist', lazy=True)  

    def __repr__(self):
        return "<Wishlist %r id=[%s]>" % (self.name, self.id)

    def serialize(self):
        """ Serializes a Wishlist into a dictionary """
        wishlist = {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "date_created": self.date_joined.strftime(DATETIME_FORMAT),
            "items": []
        }
        for wishlist in self.wishlists:
            wishlist['items'].append(wishlist.serialize())
        return wishlist

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.user_id = data["user_id"]
            self.date_created = datetime.strptime(data["date_created"], DATETIME_FORMAT)
            # handle inner list of items
            item_list = data.get("items")
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