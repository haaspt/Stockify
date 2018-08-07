# Stockify

## Overview

Stockify is a simple utility for tracking portfolio performance and getting easy access to current and historical stock market data.

## Installation

Clone the repo and install with setup.py or pip:

```bash
$ git clone https://github.com/haaspt/Stockify.git
$ cd Stockify
$ python setup.py install
OR
$ pip install -e .
```

### Requirements

- [Python](https://www.python.org/downloads/) 3.6 or greater
- [Requests](http://docs.python-requests.org/en/master/)

## Usage

Stockify can be used as a portfolio tracking tool or to get stock market data directly from the IEX and Alpha Vantage APIs directly.

As a portfolio tracker:

```python
>>> import Stockify
>>> portfolio = Stockify.Portfolio(['aapl','ms'])
>>> portfolio['aapl'].add_lot('2018-01-01', 123.45, 8)
>>> ms_lots = [['2018-12-31', 23.45, 2], ['2018-11-01', 30.00, 1]]
>>> portfolio['ms'].add_lots(ms_lots)
>>> portfolio.get_prices()
[{'AAPL': 209.015}, {'MS': 49.975}]
>>> portfolio['aapl'].get_value()
1672.12
```

As an API wrapper:

```python
>>> from Stockify import Data, HistoricalData
>>> Data.price('aapl')
209.015
>>> historical = HistoricalData('api_credentials')
>>> historical.stock('aapl', 'day')
# Returns ~1mo of daily price data
```

## Credits

Stockify relies on the [IEX](https://iextrading.com/) API for real-time stock data: Data provided free by [IEX](https://iextrading.com/developer). View [IEX's Terms of Use](https://iextrading.com/api-exhibit-a/)

Stockify relies on the [Alpha Vantage](https://www.alphavantage.co) API for historical data. Please see [their Terms of Service](https://www.alphavantage.co/terms_of_service/) for more.

## Disclaimer

Stockify and the information provided by it is for information and education purposes only and is not intended for trading purposes or advice.