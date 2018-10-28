import json
import unittest
import requests

from webapp import app


class TailsTestCase(unittest.TestCase):
    """Class for testing the pricing api"""

    def setUp(self):
        """Define the test variables and setup the app."""
        self.client = app.test_client

    def test_pricing_calculation_foo_dict(self):
        """Test the API for pricing calculation (POST request)"""

        # test passing an invalid json
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(dict(foo='bar')),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn(u"Missing order key", res.data)

    def test_pricing_calculation_missing_order_id(self):
        # test passing a missing order id json
        data = {
            "order": {
                "customer": {
                    "customer_id": 1,
                },
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 1,
                    },
                ],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn(u"Missing order id", res.data)

    def test_pricing_calculation_empty_item_list(self):
        # test passing an empty items list
        data = {
            "order": {
                "id": 12345,
                "customer": {
                    "customer_id": 1,
                },
                "items": [],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn(u"Empty items list", res.data)

    def test_pricing_calculation_missing_product_id(self):
        # test passing a missing product_id in the items list
        data = {
            "order": {
                "id": 12345,
                "customer": {
                    "customer_id": 1,
                },
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 1,
                    },
                    {
                        "quantity": 1,
                    },
                ],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn(u"Malformed items list. product_id is missing for at least one item", res.data)

    def test_pricing_calculation_missing_quantity(self):
        # test passing a missing quantity in the items list
        data = {
            "order": {
                "id": 12345,
                "customer": {
                    "customer_id": 1,
                },
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 1,
                    },
                    {
                        "product_id": 2,
                    },
                ],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn(u"Malformed items list. quantity is missing for at least one item", res.data)

    def test_pricing_calculation_missing_currency(self):
        # test passing a missing currency order
        data = {
            "order": {
                "id": 12345,
                "customer": {
                    "customer_id": 1,
                },
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 1,
                    },
                    {
                        "product_id": 2,
                        "quantity": 2,
                    },
                ],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(u"GBP", data[u'currency'])

    def test_pricing_calculation_duplicated_product(self):
        # test passing an item list with duplicated product
        data = {
            "order": {
                "id": 12345,
                "customer": {
                    "customer_id": 1,
                },
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 2,
                    },
                    {
                        "product_id": 2,
                        "quantity": 2,
                    },
                    {
                        "product_id": 1,
                        "quantity": 3,
                    },
                ],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(5, sum([d[u'quantity'] for d in data[u'items'] if d[u'product_id'] == 1]))

    def test_pricing_calculation_invalid_product(self):
        # test passing an item list with invalid product
        data = {
            "order": {
                "id": 12345,
                "customer": {
                    "customer_id": 1,
                },
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 2,
                    },
                    {
                        "product_id": 2,
                        "quantity": 2,
                    },
                    {
                        "product_id": 999,
                        "quantity": 3,
                    },
                ],
            }
        }
        res = self.client().post('/api/v1/pricing_info',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn(u'Malformed items list, invalid product type detected', res.data)

# Make the tests executable
if __name__ == "__main__":
    unittest.main()
