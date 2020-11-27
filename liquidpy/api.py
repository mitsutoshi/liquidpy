from datetime import datetime
import json
import jwt
import requests
from requests.exceptions import HTTPError

from typing import Dict, Any, List


BASE_URL: str = 'https://api.liquid.com'
"""API Base URL"""


MIN_ORDER_QUANTITY: float = 0.001
"""minimum order quantity"""


PRODUCT_ID_BTCJPY: int = 5
"""Product ID: BTC/JPY"""


PRODUCT_ID_ETHJPY: int = 29
"""Product ID: ETH/JPY"""


PRODUCT_ID_XRPJPY: int = 83
"""Product ID: XRP/JPY"""


PRODUCT_ID_BCHJPY: int = 41
"""Product ID: BCH/JPY"""


PRODUCT_ID_QASHJPY: int = 50
"""Product ID: QASH/JPY"""


class Liquid(object):

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError('api_key and api_secret are required.')
        self.api_key = api_key
        self.api_secret = api_secret
        self.s = requests.Session()

    def __del__(self):
        self.s.close()

    def _create_auth_headers(self, path: str) -> dict:
        '''
        _create_auth_headers creates authentication header to call private API

        Parameters
        ----------
        path: str
            API path included in URI

        Returns
        -------
        dict
            Authentication headers to use private API
        '''
        payload = {
            'path': path,
            'nonce': int(datetime.now().timestamp() * 1000),
            'token_id': self.api_key
        }
        return {
                'X-Quoine-Auth': jwt.encode(payload, self.api_secret, algorithm='HS256'),
                'X-Quoine-API-Version': '2',
                'Content-Type': 'application/json'
                }

    def get_products(self, product_id: int = 0) -> Dict[str, Any]:
        path = '/products' + (f'/{product_id}' if product_id else '')
        res = self.s.get(BASE_URL + path)
        if not res.ok:
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        return json.loads(res.text)

    def get_accounts_balance(self) -> Dict[str, Any]:
        path = '/accounts/balance'
        res = self.s.get(BASE_URL + path, headers=self._create_auth_headers(path))
        if not res.ok:
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        return json.loads(res.text)

    def get_orders(self, status: str = None):
        path = '/orders' + (f'?status={status}' if status else "")
        res = self.s.get(BASE_URL + path, headers=self._create_auth_headers(path))
        if not res.ok:
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        return json.loads(res.text)['models']

    def cancel_order(id: str) -> None:
        path = f"/orders/{o['id']}/cancel"
        res = self.s.put(BASE_URL + path, headers=self._create_auth_headers(path))
        if not res.ok:
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')

    def create_order(self, product_id: int, side: str, price: int, quantity: float):
        data = {
                'order': {
                    'order_type': 'limit',
                    'product_id': product_id,
                    'side': side,
                    'price': price,
                    'quantity': quantity
                    }
                }
        headers = self._create_auth_headers('/orders/')
        res = self.s.post(
                BASE_URL + '/orders/', data=json.dumps(data), headers=headers)
        if not res.ok:
            print(f'Failed to create an order. [product_id={product_id}, side={side}, price={price}, quantity={quantity}]')
            raise HTTPError(f'status: {res.status_code}: text: {res.text}')
        print(f'Order has been created. [product_id={product_id}, side={side}, price={price}, quantity={quantity}]')
