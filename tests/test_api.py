import unittest
from datetime import datetime
import freezegun
import jwt
from liquidpy.api import Liquid, PRODUCT_ID_BTCJPY


class TestApi(unittest.TestCase):

    def setUp(self):
        self.api_key = 'dummy_key'
        self.api_secret = 'dummy_secret'
        self.api = Liquid(api_key=self.api_key, api_secret=self.api_secret)

    @freezegun.freeze_time('2015-10-21 12:34:56')
    def test_create_auth_headers(self):
        path = '/hoge'
        sign = jwt.encode(
                {
                    'path': path,
                    'nonce': int(datetime.now().timestamp() * 1000),
                    'token_id': self.api_key
                },
                self.api_secret,
                algorithm='HS256')
        headers = self.api._create_auth_headers(path)
        self.assertEqual(headers['X-Quoine-Auth'], sign)
        self.assertEqual(headers['X-Quoine-API-Version'], '2')
        self.assertEqual(headers['Content-Type'], 'application/json')

    def test_get_products(self):
        res = self.api.get_products()
        self.assertTrue(type(res) == list)
        for p in res:
            self.assertTrue('id' in p)

    def test_get_product(self):
        res = self.api.get_products(product_id=PRODUCT_ID_BTCJPY)
        self.assertTrue(type(res) == dict)
        self.assertTrue('id' in res)
        self.assertEqual(int(res['id']), PRODUCT_ID_BTCJPY)

