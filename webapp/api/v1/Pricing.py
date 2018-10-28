# -*- coding: utf-8 -*-
from itertools import groupby

from flask import json

# local import
from webapp import app, cache
from webapp.api.v1.Currency import Currency

"""Pricing class

This class contain all function to manage the price list

Todo:
    * Write a better description

"""


class Pricing(object):
    MEMCACHE_TIMEOUT = 60 * 60
    DEFAULT_CURRENCY = u"GBP"  # type: unicode

    @classmethod
    def load_from_json(cls, json_uri=None):
        """Get the pricelist from the specified json file and load in memcache

        Args:
            json_uri: The uri of the pricelist file.

        Raises:
            An exception if the operation fails

        """

        if json_uri is None:
            json_uri = app.config['PRICING_JSON_URI']

        try:
            data = json.load(open(json_uri))

            products = {}
            for p in data[u'prices']:
                products.update({
                    p[u'product_id']: {
                        k: v for k, v in p.iteritems()
                    }
                })

            cache.set(u'PRODUCTS', products, cls.MEMCACHE_TIMEOUT)
            cache.set(u'VAT_BANDS', data[u'vat_bands'], cls.MEMCACHE_TIMEOUT)
        except Exception as e:
            raise Exception(u'Unable to load the data from {}: {}'.format(json_uri, e.message))

    @classmethod
    def get_products(cls):
        """Get the list of products from memcache is present otherwise from json file

        Raises:
            An exception if the operation fails

        """

        # try to get from memcache
        products = cache.get(u'PRODUCTS')
        if products:
            return products

        # not found in memcache, get the data from json file
        Pricing.load_from_json()

        products = cache.get(u'PRODUCTS')
        return products

    @classmethod
    def get_vat_bands(cls):
        """Get the list of products from memcache is present otherwise from json file

        Raises:
            An exception if the operation fails

        """

        # try to get from memcache
        vat_bands = cache.get(u'VAT_BANDS')
        if vat_bands:
            return vat_bands

        # not found in memcache, get the data from json file
        Pricing.load_from_json()

        vat_bands = cache.get(u'VAT_BANDS')
        return vat_bands

    @classmethod
    def get_totals(cls, data):
        """Calculate order totals, the returned data include:
            - the total price for the order
            - the total VAT for the order
            - price and VAT for each item in the order

        Args:
            A json structure containing at least the above info:
            {
                "order": {
                    "id": ...,
                    "customer": {
                        "customer_id": ...,
                        "name": ...,
                        "surname": ...,
                    },
                    "items": [
                        {
                            "product_id": ...,
                            "quantity": ...,
                        },
                    ],
                    "currency": ...   # if missing GBP is used
                }
            }

        Raises:
            An exception if the operation fails

        """
        # check for json syntax - order key
        try:
            order = data[u'order']
        except KeyError:
            raise Exception({u"code": 400, u"text": u'Missing order key'})

        # check for json syntax - order key
        try:
            order_id = order[u'id']
        except KeyError:
            raise Exception({u"code": 400, u"text": u'Missing order id'})

        # check for json syntax - items
        try:
            items = order[u'items']
        except KeyError:
            raise Exception({u"code": 400, u"text": u'Missing items list'})

        if not items:
            raise Exception({u"code": 400, u"text": u'Empty items list'})

        # check if there are missing product_id in the items list
        if [i for i in items if "product_id" not in i.keys()]:
            raise Exception({
                u"code": 400,
                u"text": u'Malformed items list. product_id is missing for at least one item'
            })

        # check if there are missing quantity in the items list
        if [i for i in items if "quantity" not in i.keys()]:
            raise Exception({
                u"code": 400,
                u"text": u'Malformed items list. quantity is missing for at least one item'
            })

        # check for currency if not present use class default
        currency = order.get(u'currency', cls.DEFAULT_CURRENCY)
        order['currency'] = currency

        # check if a product is duplicated group by and sum the quantity
        items = sorted(items, key=lambda x: x[u'product_id'])
        grouped = []
        for k, values in groupby(items, lambda x: x[u'product_id']):
            grouped.append({
                k: sum([v[u'quantity'] for v in list(values)])
            })
        # -> more compact version of the above one but very difficult to read
        # grouped = {
        #     k: sum([v['quantity'] for v in list(values)]) for k, values in groupby(items, lambda x: x[u'product_id'])
        # }

        # rebuild the given list of dict without duplicate product_id
        items = [{
                u'product_id': k,
                u'quantity': v,
            } for g in grouped for k, v in g.items()]

        # get the price for each product_id
        products = Pricing.get_products()

        # chek for invalid product id
        invalid = [item[u'product_id'] for item in items if item[u'product_id'] not in products.keys()]
        if invalid:
            raise Exception({
                u"code": 400,
                u"text": u'Malformed items list, invalid product type detected: {}'.format(', '.join([str(i) for i in invalid]))
            })

        # get the value for the vat bands
        vats = Pricing.get_vat_bands()

        # get the exchange rate for current currency
        rate = Currency.get_exchange_rate(currency)

        # add all the info for the final calculation
        for item in items:
            id = item[u'product_id']
            for k, v in products[id].iteritems():
                if k == u'price':
                    # calculate the price for the given currency
                    item[u'price'] = round(v * rate, 2)
                elif k == u'product_id':
                    # skip the product_id
                    pass
                elif k == u'vat_band':
                    # get the value for the given vat band
                    try:
                        item[u'vat'] = vats[v]
                    except KeyError:
                        raise Exception({
                            u"code": 400,
                            u"text": u'Invalid "{}" {} for product {}'.format(v, k, id)})
                else:
                    # add any other info from the json file for the product
                    item[k] = v

        # do the calculation for each item
        for item in items:
            item[u'item_price'] = round(item[u'price'] * item[u'quantity'], 2)
            item[u'item_vat'] = round(item[u'item_price'] * item[u'vat'], 2)

        order[u'items'] = items
        order[u'order_total_price'] = round(sum([i[u'item_price'] for i in items]), 2)
        order[u'order_total_vat'] = round(sum([i[u'item_vat'] for i in items]), 2)

        return order
