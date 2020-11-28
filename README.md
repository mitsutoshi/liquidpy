# liquidpy

liquidpy is the Python library for trading cryptocurrency with the Liquid by Quoine.

if you need detail information about Liquid's API, please see [Liquid official API document](https://developers.liquid.com/)

## Install

```
pip install git+https://github.com/mitsutoshi/liquidpy#egg=liquidpy
```

## How to use

Create Liquid object. _API_KEY_ and _API_SECRET_ are required if you use private API.

```python
from liquidpy.api import Liquid
liquid = Liquid(api_key='xxx', api_secret='xxx')
```

### Public API

#### Get products

`get_products` calls `/products`.

```python
products = liquid.get_products()
for p in products:
    print(p['product_id'])
    print(p['currency_pair_code'])
```

#### Get a product

`get_products` with product_id calls `/products/{product_id}`.

```python
p = liquid.get_products(product_id=5)
print(p['product_id'])          # 5
print(p['currency_pair_code'])  # BTCJPY
```

### Private API 🔑

Private API reuqires to authenticate. If you call it without authentication, exception will be thrown.

#### Get accounts balance

`get_accounts_balnace` calls `/accounts/balance`.

```python
accounts_balance = liquid.get_accounts_balnace()
for b in accounts_balance:
    print(b['currency'])
    print(b['balance'])
```

#### Get own orders

```python
```

#### Create an order

Create an market type order.

e.g.
* product: 5 (BTCJPY)
* side: buy
* quantity: 0.01

```python
from liquidpy.api import SIDE_BUY
res = liquid.create_order(product_id=5, side=SIDE_BUY, quantity=0.01)
print(f"order_id: {res['id']}")
```

Create an limit type order.

e.g.
* product: 5 (BTCJPY)
* side: buy
* price: 1000000
* quantity: 0.01

```python
from liquidpy.api import SIDE_BUY
res = liquid.create_order(product_id=5, side=SIDE_BUY, quantity=0.01, price=1000000)
print(f"order_id: {res['id']}")
```

#### Cancel an order

Cancel an order of id=1234.

```python
liquid.cancel_order(id=1234)
```
