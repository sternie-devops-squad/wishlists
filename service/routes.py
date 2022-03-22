# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Wishlist Service

This microservice handles the lifecycle of Wishlists
"""
import os
import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from werkzeug.exceptions import NotFound
from service.models import Wishlist, Item, DataValidationError
from . import status  # HTTP Status Codes
from . import app  # Import Flask application


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

# ######################################################################
# # LIST ALL WISHLISTS
# ######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """ Returns all of the Wishlists """
    app.logger.info("Request for Wishlist list")
    wishlists = []
    name = request.args.get("name")
    if name:
        wishlists = Wishlist.find_by_name(name)
    else:
        wishlists = Wishlist.all()

    results = [wishlist.serialize() for wishlist in wishlists]
    return make_response(jsonify(results), status.HTTP_200_OK)


# ######################################################################
# # RETRIEVE AN WISHLIST
# ######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist

    This endpoint will return an Wishlist based on it's id
    """
    app.logger.info("Request for Wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' could not be found.")

    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates an Wishlist
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

######################################################################
# UPDATE (EDIT) AN EXISTING WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlist(wishlist_id):
    """
    Update a wishlist

    This endpoint will update a wishlist based the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    wishlist.deserialize(request.get_json())
    wishlist.id = wishlist_id
    wishlist.update()

    app.logger.info("Wishlist with ID [%s] updated.", wishlist.id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete an Wishlist
    This endpoint will delete an Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

#---------------------------------------------------------------------
#                I T E M   M E T H O D S
#---------------------------------------------------------------------

######################################################################
# LIST ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_items(wishlist_id):
    """ Returns all of the Itemes for an Wishlist """
    app.logger.info("Request for all Itemes for Wishlist with id: %s", wishlist_id)

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' could not be found.")

    results = [item.serialize() for item in wishlist.items]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# ADD AN ITEM TO A WISHLIST
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items', methods=['POST'])
def create_items(wishlist_id):
    """
    Create an Item on an Wishlist
    This endpoint will add an item to an wishlist
    """
    app.logger.info("Request to create an Item for Wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' could not be found.")

    item = Item()
    item.deserialize(request.get_json())
    wishlist.items.append(item)
    wishlist.update()
    message = item.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)

######################################################################
# RETRIEVE AN Item FROM ACCOUNT
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items/<int:item_id>', methods=['GET'])
def get_items(wishlist_id, item_id):
    """
    Get an Item
    This endpoint returns just an item
    """
    app.logger.info("Request to retrieve Item %s for Wishlist id: %s", (item_id, wishlist_id))

    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{item_id}' could not be found.")

    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN Item
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_items(wishlist_id, item_id):
    """
    Update an Item
    This endpoint will update an Item based the body that is posted
    """
    app.logger.info("Request to update Item %s for Wishlist id: %s", (item_id, wishlist_id))
    check_content_type("application/json")

    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{item_id}' could not be found.")

    item.deserialize(request.get_json())
    item.id = item_id
    item.update()
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE AN Item
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(wishlist_id, item_id):
    """
    Delete an Item
    This endpoint will delete an Item based the id specified in the path
    """
    app.logger.info("Request to delete Item %s for Wishlist id: %s", (item_id, wishlist_id))

    item = Item.find(item_id)
    if item:
        item.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Wishlist.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}")