from datetime import datetime
from logging import getLogger, Logger
from typing import Dict, Any, List
import json
import jwt
import requests
from requests.exceptions import HTTPError


BASE_URL: str = 'https://api.liquid.com'
"""API Base URL"""


SIDE_BUY: str = 'buy'
"""Side: buy"""


SIDE_SELL: str = 'sell'
"""Side: sell"""


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


ORDER_STATUS_LIVE: str = 'live'
"""Order status: live"""


ORDER_STATUS_CANCELLED: str = 'cancelled'
"""Order status: cancelled"""


ORDER_STATUS_FILLED: str = 'filled'
"""Order status: filled"""


ORDER_STATUS_FILLED: str = 'partially_filled'
"""Order status: partially_filled"""


logger: Logger = getLogger(__name__)


def privateapi(func):
    def wrapper(self, *args, **kwargs):
        if not self.api_key or not self.api_secret:
            raise ValueError('api_key and api_secret are required.')
        return func(self, *args, **kwargs)
    return wrapper


class Liquid(object):
    '''
    Liquid REST API Client
    '''

    def __init__(self, api_key: str = None, api_secret: str = None):
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
            logger.error(f'Failed to get products.')
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        return json.loads(res.text)

    @privateapi
    def get_accounts_balance(self) -> Dict[str, Any]:
        path = '/accounts/balance'
        res = self.s.get(BASE_URL + path, headers=self._create_auth_headers(path))
        if not res.ok:
            logger.error(f'Failed to get accounts balance.')
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        return json.loads(res.text)

    @privateapi
    def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        path = '/orders' + (f'?status={status}' if status else "")
        res = self.s.get(BASE_URL + path, headers=self._create_auth_headers(path))
        if not res.ok:
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        return json.loads(res.text)['models']

    @privateapi
    def cancel_order(self, id: str) -> None:
        path = f"/orders/{id}/cancel"
        res = self.s.put(BASE_URL + path, headers=self._create_auth_headers(path))
        if not res.ok:
            logger.error(f'Failed to cancel order. [id={id}]')
            raise HTTPError(f'status: {res.status_code}, text: {res.text}')
        logger.info(f'Order has been cancelled. [id={id}]')

    @privateapi
    def create_order(self, product_id: int, side: str, quantity: float, price: int = None) -> Dict[str, Any]:
        if quantity < MIN_ORDER_QUANTITY:
            raise ValueError(f'Order quantity {quantity:.8f} is too small. Specify {MIN_ORDER_QUANTITY} or more.')

        order = {
                'product_id': product_id,
                'side': side,
                'quantity': quantity
                }
        if price:
            order.update({
                'order_type': 'limit',
                'price': price
                })
        else:
            order.update({
                'order_type': 'market'
                })

        headers = self._create_auth_headers('/orders/')
        res = self.s.post(
                BASE_URL + '/orders/', data=json.dumps({'order': order}), headers=headers)
        if not res.ok:
            logger.error(f'Failed to create an order. [product_id={product_id}, side={side}, price={price}, quantity={quantity}]')
            raise HTTPError(f'status: {res.status_code}: text: {res.text}')
        body = json.loads(res.text)
        logger.info(f"Order has been created. [order_id={body['id']}, product_id={product_id}, side={side}, price={price}, quantity={quantity}]")
        return body
