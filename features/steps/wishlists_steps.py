"""
Wishlist Steps
Steps file for wishlists.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following wishlists')
def step_impl(context):
    """ Delete all Wishlists and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the wishlists and delete them one by one
    context.resp = requests.get(context.base_url + '/wishlists', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for pet in context.resp.json():
        context.resp = requests.delete(context.base_url + '/wishlists/' + str(wishlist["_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new wishlists
    create_url = context.base_url + '/wishlists'
    for row in context.table:
        data = {
            "name": row['name'],
            "type": row['type'],
            "user_id": row['user_id'] in ['True', 'true', '1'],
            "created_date": row['created_date'],
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


 