from flask import Blueprint, jsonify, request
from webapp.api.v1.Currency import Currency
from webapp.api.v1.Pricing import Pricing

mod_api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@mod_api_v1.route('/products', methods=['GET'])
def products():
    """Get the full list of products
    """
    try:
        prods = Pricing.get_products()
        return jsonify(prods), 200
    except Exception as e:
        return jsonify(e.message), 500


@mod_api_v1.route('/product/<int:product_id>', methods=['GET'])
def product(product_id):
    """Get the details of the product given id

       Args:
           product_id: The id of the product

       Return:
           All the info of the products
    """

    try:
        prods = Pricing.get_products()
        prod = prods[product_id]
        return jsonify(prod), 200
    except KeyError:
        return jsonify(u'product_id not found: {}'.format(product_id)), 500
    except Exception as e:
        return jsonify(e.message), 500


@mod_api_v1.route('/vat_bands', methods=['GET'])
def vat_bands():
    """Get the full list of vat bands
    """
    try:
        vats = Pricing.get_vat_bands()
        return jsonify(vats), 200
    except Exception as e:
        return jsonify(e.message), 500


@mod_api_v1.route('/vat_band/<vat_band_id>', methods=['GET'])
def vat_band(vat_band_id):
    """Get vat band of given id
       Args:
           vat_band_id: The id of the vat band

       Return:
           The value of the given vat band
    """

    try:
        vats = Pricing.get_vat_bands()
        vat = vats[vat_band_id]
        return jsonify(vat), 200
    except KeyError:
        return jsonify(u'vat_band_id not found: {}'.format(vat_band_id)), 500
    except Exception as e:
        return jsonify(e.message), 500


@mod_api_v1.route('/currencies', methods=['GET'])
def currencies():
    """Get the full list of valid currencies
    """
    try:
        currs = Currency.get_currencies()
        return jsonify(currs), 200
    except Exception as e:
        return jsonify(e.message), 500


@mod_api_v1.route('/currency_rate/<currency>', methods=['GET'])
def currency_rate(currency):
    """Get the exchange rate for GBP to given currency
    """
    try:
        rate = Currency.get_exchange_rate(currency)
        return jsonify(rate), 200
    except Exception as e:
        return jsonify(e.message), 500


@mod_api_v1.route('/pricing_info', methods=['POST'])
def pricing_info():

    if not request.is_json:
        return jsonify(u'Invalid request format - only json accepted'), 400

    try:
        order = Pricing.get_totals(request.json)
        return jsonify(order), 200
    except Exception as e:
        return jsonify(e.message[u'text']), e.message[u'code']
