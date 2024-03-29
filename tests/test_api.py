import unittest
import os
from datetime import datetime
import freezegun
import jwt
from liquidpy.api import *


class TestApi(unittest.TestCase):

    def setUp(self):
        self.api_key = os.environ.get('LIQUID_API_KEY', '')
        self.api_secret = os.environ.get('LIQUID_API_SECRET', '')
        self.api = Liquid(api_key=self.api_key, api_secret=self.api_secret)
        self.api = Liquid()

    def test_init(self):

        apikey = 'apikey'
        apisecret = 'apisecret'

        # 1. env
        os.environ['LIQUID_API_KEY'] = apikey
        os.environ['LIQUID_API_SECRET'] = apisecret
        lqd = Liquid()
        self.assertEqual(os.getenv('LIQUID_API_KEY'), lqd.api_key)
        self.assertEqual(os.getenv('LIQUID_API_SECRET'), lqd.api_secret)
        del os.environ['LIQUID_API_KEY']
        del os.environ['LIQUID_API_SECRET']

        # 2. argument
        lqd = Liquid(api_key=apikey, api_secret=apisecret)
        self.assertEqual(apikey, lqd.api_key)
        self.assertEqual(apisecret, lqd.api_secret)

        # 3. not specified
        lqd = Liquid()
        self.assertEqual('', lqd.api_key)
        self.assertEqual('', lqd.api_secret)

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

    def test_get_product_BTCJPY(self):
        res = self.api.get_products(product_id=PRODUCT_ID_BTCJPY)
        self.assertTrue(type(res) == dict)
        self.assertTrue('id' in res)
        self.assertEqual(int(res['id']), PRODUCT_ID_BTCJPY)
        self.assertEqual(res['currency_pair_code'], 'BTCJPY')

    def test_get_product_ETHJPY(self):
        self.__test_get_product(PRODUCT_ID_ETHJPY, 'ETHJPY')

    def test_get_product_XRPJPY(self):
        self.__test_get_product(PRODUCT_ID_XRPJPY, 'XRPJPY')

    def test_get_product_BCHJPY(self):
        self.__test_get_product(PRODUCT_ID_BCHJPY, 'BCHJPY')

    def test_get_product_QASHJPY(self):
        self.__test_get_product(PRODUCT_ID_QASHJPY, 'QASHJPY')

    def __test_get_product(self, product_id, currency_pair_code):
        res = self.api.get_products(product_id=product_id)
        self.assertTrue(type(res) == dict)
        self.assertTrue('id' in res)
        self.assertEqual(int(res['id']), product_id)
        self.assertEqual(res['currency_pair_code'], currency_pair_code)

    def test_get_accounts_balance_autherr(self):
        api = Liquid()
        try:
            api.get_accounts_balance()
        except Exception as e:
            self.assertEqual(type(e), ValueError)

    def test_get_orders_autherr(self):
        api = Liquid()
        try:
            api.get_orders()
        except Exception as e:
            self.assertEqual(type(e), ValueError)

    def test_create_order_autherr(self):
        api = Liquid()
        try:
            pid = PRODUCT_ID_BTCJPY
            api.create_order(product_id=pid, side='Buy', price=0, quantity=MIN_ORDER_QUANTITY[pid] - 0.01)
        except Exception as e:
            self.assertEqual(type(e), ValueError)

    def test_get_accounts_balance(self):
        if self.api_key and self.api_secret:
            res = self.api.get_accounts_balance()
            self.assertEqual(type(res), list)
            for b in res:
                self.assertTrue('currency' in b)
                self.assertTrue('balance' in b)
        else:
            print('skip test as API_KEY and API_SECRET are not defined')

    def test_create_order_quantityerr(self):
        satoshi = 0.00000001
        try:
            pid = PRODUCT_ID_BTCJPY
            self.api.create_order(
                    product_id=pid, side=SIDE_BUY, quantity=MIN_ORDER_QUANTITY[pid] - satoshi, price=1)
            self.fail('Exception has not occurred.')
        except ValueError as e:
            pass

    @unittest.skip("This test creates an order actually")
    def test_create_order_limit(self):

        # get a latest price
        p = self.api.get_products(product_id=PRODUCT_ID_BTCJPY)

        # set a price that is not executed
        price = int(float(p['last_traded_price']) - 300000)

        # create an order
        pid = PRODUCT_ID_BTCJPY
        res = self.api.create_order(
                product_id=pid, side=SIDE_BUY, quantity=MIN_ORDER_QUANTITY[pid], price=price)
        self.assertIsNotNone(res['id'])
        self.assertEqual(res['product_id'], PRODUCT_ID_BTCJPY)
        self.assertEqual(res['order_type'], 'limit')
        self.assertEqual(res['side'], SIDE_BUY)
        self.assertEqual(int(res['price']), price)
        self.assertEqual(res['quantity'], str(MIN_ORDER_QUANTITY[pid]))

        # cancel an order
        self.api.cancel_order(id=res['id'])

    def test_get_fiat_deposits(self):
        currency = 'JPY'
        if self.api_key and self.api_secret:
            res = self.api.get_fiat_deposit_requests(currency=currency)
            self.assertEqual(type(res), dict)
            for m in res['models']:
                if 'currency' in m:
                    self.assertEqual(m['currency'], currency)
                    self.assertGreater(float(m['amount']), 0)
        else:
            print('skip test as API_KEY and API_SECRET are not defined')

    def test_get_fiat_deposits_history(self):
        currency = 'JPY'
        if self.api_key and self.api_secret:
            res = self.api.get_fiat_deposits_history(currency=currency)
            self.assertEqual(type(res), dict)
            for m in res['models']:
                if 'currency' in m:
                    self.assertEqual(m['currency'], currency)
                    self.assertGreater(float(m['net_amount']), 0)
        else:
            print('skip test as API_KEY and API_SECRET are not defined')

    def test_get_executions_me(self):
        if self.api_key and self.api_secret:
            limit = 1
            page = 1
            executions = self.api.get_executions_me(product_id=PRODUCT_ID_BTCJPY, page=page, limit=limit)
            self.assertEqual(page, executions['current_page'])
            self.assertEqual(limit, len(executions['models']))

            limit = 2
            executions = self.api.get_executions_me(product_id=PRODUCT_ID_BTCJPY, page=page, limit=limit)
            self.assertEqual(page, executions['current_page'])
            self.assertEqual(limit, len(executions['models']))

            limit = 2
            page = 2
            executions = self.api.get_executions_me(product_id=PRODUCT_ID_BTCJPY, page=page, limit=limit)
            self.assertEqual(page, executions['current_page'])
            self.assertEqual(limit, len(executions['models']))
        else:
            print('skip test as API_KEY and API_SECRET are not defined')

    def test_get_orders(self):

        if self.api_key and self.api_secret:

            # status, side, funding_currency, product_id
            pattern = [
                    (ORDER_STATUS_LIVE, None, None, None),
                    (ORDER_STATUS_LIVE, SIDE_BUY, None, None),
                    (ORDER_STATUS_LIVE, SIDE_SELL, None, None),
                    (ORDER_STATUS_FILLED, None, None, None),
                    (ORDER_STATUS_CANCELLED, None, None, None),
                    (None, None, FUNDING_CURRENCY_USD, None),
                    (None, None, FUNDING_CURRENCY_JPY, None),
                    (PRODUCT_ID_BTCJPY, None, None, None),
                    (PRODUCT_ID_SOLJPY, None, None, None),
                    ]

            api = Liquid()

            for status, side, funding_currency, product_id in pattern:

                orders = api.get_orders(
                        status=status,
                        side=side,
                        funding_currency=funding_currency,
                        product_id=product_id)

                for o in orders:

                    # check status and side
                    if status == ORDER_STATUS_LIVE:
                        self.assertEqual(o['status'], status)
                        self.assertEqual(o['side'], status)
                    elif status == ORDER_STATUS_FILLED:
                        self.assertEqual(o['status'], status)
                    elif status == ORDER_STATUS_CANCELLED:
                        self.assertEqual(o['status'], status)

                    # check funding currency
                    if funding_currency:
                        self.assertEqual(o['funding_currency'], funding_currency)

                    if product_id:
                        self.assertEqual(o['product_id'], product_id)
        else:
            print('skip test as API_KEY and API_SECRET are not defined')
