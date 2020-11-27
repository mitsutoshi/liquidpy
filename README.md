# liquidpy

liquidpy is the API library for trading cryptocurrency with the Liquid by Quoine.

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
```

#### Get a product

`get_products` with product_id calls `/products/{product_id}`.

```python
products = liquid.get_products(product_id=5)
```

### Private API 🔑

Private API reuqires to authenticate. If you call it without authentication, exception will be thrown.

#### Get accounts balance

`get_accounts_balnace` calls `/accounts/balance`.

```python
accounts_balance = liquid.get_accounts_balnace()
```

#### Get own orders

```python
```

#### Create an order

```python
```

#### Cancel an order

```python
```
