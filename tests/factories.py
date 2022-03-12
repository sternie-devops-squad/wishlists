# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Test Factory to make fake objects for testing
"""
import factory
from datetime import datetime
from factory.fuzzy import FuzzyChoice
from service.models import Wishlist, Item

class ItemFactory(factory.Factory):
    """ Creates fake Items """

    class Meta:
        model = Item

    id = factory.Sequence(lambda n: n)
#    wishlist_id = ???
    name = FuzzyChoice(choices=["book", "basketball", "other"])
    category = FuzzyChoice(choices=["home decor", "sports", "music", "apparel"])
    price = FuzzyChoice(choices=[5,10,15,20,25,50,75,100])
    in_stock = FuzzyChoice(choices=[True, False])
    purchased = FuzzyChoice(choices=[True, False])


class WishlistFactory(factory.Factory):
    """ Creates fake Wishlists """

    class Meta:
        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["personal", "gifts", "home improvement"])
    user_id = FuzzyChoice(choices=[1, 2])
    created_date = factory.LazyFunction(datetime.utcnow)
