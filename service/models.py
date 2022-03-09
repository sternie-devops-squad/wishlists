# Copyright 2016, 2021 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Wishlist Service
All of the models are stored in this module

Models
------
Wishlist - A wishlist used to store items desired to be bought

Attributes:
-----------
id (string) - the id of the wishlist
name (string) - the name of the wishlist
user (int) - the id of the user the wishlist 'belongs to'
items (boolean) - the list of items stored in the wishlist


"""
import logging
from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Wishlist.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""

class Wishlist(db.Model):
    """
    Class that represents a Wishlist

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    category = db.Column(db.String(63), nullable=False)
    user = db.Column(db.Integer)
    favorite = db.Column(db.Boolean(), nullable=False, default=False)

    ##TODO: Add list of items here

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return "<Wishlist %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Wishlist to the database
        """
        logger.info("Creating %s", self.name)
        # id must be none to generate next primary key
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Wishlist to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Wishlist from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Wishlist into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "user": self.user,
            "favorite": self.favorite,
            #TODO: "items": [],
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Wishlist from a dictionary
        Args:
            data (dict): A dictionary containing the Wishlist data
        """
        try:
            self.id = data["id"]
            self.name = data["name"]
            self.category = data["category"]
            self.user = data["user"]
            #wishlist_items
            if isinstance(data["favorite"], bool):
                self.favorite = data["favorite"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [favorite]: "
                    + str(type(data["favorite"]))
                )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid wishlist: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid wishlist: body of request contained bad or no data " + str(error)
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """Returns all of the Wishlist in the database"""
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, wishlist_id: int):
        """Finds a Wishlist by it's ID

        :param wishlist_id: the id of the Wishlist to find
        :type wishlist_id: int

        :return: an instance with the wishlist_id, or None if not found
        :rtype: Wishlist

        """
        logger.info("Processing lookup for id %s ...", wishlist_id)
        return cls.query.get(wishlist_id)

    @classmethod
    def find_or_404(cls, wishlist_id: int):
        """Find a Wishlist by it's id

        :param wishlist_id: the id of the Wishlist to find
        :type wishlist_id: int

        :return: an instance with the wishlist_id, or 404_NOT_FOUND if not found
        :rtype: Wishlist

        """
        logger.info("Processing lookup or 404 for id %s ...", wishlist_id)
        return cls.query.get_or_404(wishlist_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Wishlists with the given name

        :param name: the name of the Wishlists you want to match
        :type name: str

        :return: a collection of Wishlists with that name
        :rtype: list

        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
    
    @classmethod
    def find_by_category(cls, category: str) -> list:
        """Returns all of the Wishlists in a category

        :param category: the category of the Wishlists you want to match
        :type category: str

        :return: a collection of Wishlists in that category
        :rtype: list

        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_user(cls, user: str) -> list:
        """Returns all of the Wishlists for a user

        :param user: the user of the Wishlists you want to match
        :type user: str

        :return: a collection of Wishlists in that user
        :rtype: list

        """
        logger.info("Processing user query for %s ...", user)
        return cls.query.filter(cls.user == user)

    @classmethod
    def find_by_favorite(cls, favorite: bool = True) -> list:
        """Returns all Wishlists by their favorite status

        :param favorite: True for wishlists that are favorited
        :type favorite: str

        :return: a collection of wishlists that are favorite
        :rtype: list

        """
        logger.info("Processing favorite query for %s ...", favorite)
        return cls.query.filter(cls.favorite == favorite)

    # @classmethod
    # def find_by_gender(cls, gender: Gender = Gender.UNKNOWN) -> list:
    #     """Returns all Pets by their Gender

    #     :param gender: values are ['MALE', 'FEMALE', 'UNKNOWN']
    #     :type available: enum

    #     :return: a collection of Pets that are available
    #     :rtype: list

    #     """
    #     logger.info("Processing gender query for %s ...", gender.name)
    #     return cls.query.filter(cls.gender == gender)