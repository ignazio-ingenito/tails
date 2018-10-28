"""Currency class

This class contain all the method to interact with the API from free.currencyconverterapi.com

Todo:
    * Write a better description

"""

import requests
from flask import json
from webapp import cache


class Currency(object):
    CURRENCY_LIST_URL = u'https://free.currencyconverterapi.com/api/v6/currencies'
    EXCHANGE_RATE_URL = u'https://free.currencyconverterapi.com/api/v6/convert?q={}&compact=y'

    @classmethod
    def get_currencies(cls):
        """Get the list of currencies from free.currencyconverterapi.com

        Return:
            A list of valid currencies

        """
        memcache_timeout = 60 * 30

        # try to get from memcache
        currencies = cache.get(u'CURRENCIES')
        if currencies:
            return currencies

        # not found in memcache, get from api service
        try:
            data = requests.get(cls.CURRENCY_LIST_URL)
            data = json.loads(data.content)
            cache.set(u'CURRENCIES', data['results'], timeout=memcache_timeout)

            return data['results']
        except Exception as e:
            return Exception('Unable to load the list of available currencies'.format(e.message))

    @classmethod
    def get_exchange_rate(cls, currency):
        """Get the exchange rate from GBP to given currency

           Args:
               currency: The id of the currency (3 chars)

           Return:
               The exchange rate from GBP to the given currency
        """
        memcache_timeout = 60 * 5

        currency = currency.upper()
        currencies = cls.get_currencies()

        # check if the given currency is in the allowed currencis
        if currency not in currencies:
            raise Exception('Invalid currency: {}'.format(currency))

        # set the exchange currencies
        exchange = u'GBP_{}'.format(currency)

        # try to get the exchange rate from memcache
        rate = cache.get(exchange)
        if rate:
            return rate

        # the exchange rate is not in memcache get api service
        try:
            url = cls.EXCHANGE_RATE_URL.format(exchange)
            data = requests.get(url)
            data = json.loads(data.content)
            rate = data[exchange][u'val']
        except Exception as e:
            raise Exception(u'Unable to retrieve the rate for {}'.format(e.message))

        # try to convert the rate to float
        try:
            rate = float(rate)
            cache.set(exchange, rate, memcache_timeout)
            return rate
        except Exception as e:
            raise Exception(u'Unable to convert the rate for {} -> {}: {}'.format(exchange, rate, e.message))

