"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import jsonify, request, url_for, make_response, abort

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Wishlist, Item, DataValidationError
from . import status  # HTTP Status Codes
from . import app # Import Flask application

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Wishlist REST API Service",
            version="1.0",
            paths=url_for("list_wishlists", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Wishlist.init_db(app)


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create an Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create an Wishlist")
    check_content_type("application/json")
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()
    message = wishlist.serialize()
    location_url = url_for("get_wishlists", wishlist_id=wishlist.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )