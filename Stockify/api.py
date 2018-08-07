import json
import requests
from .errors import StockifyError, StockifyAPIError

class Data(object):
    """Utility class for getting simple information about stocks

    All methods are static and no API key is required to retrieve information
    about stocks. Relies on the IEX Trading API.
    """

    @staticmethod
    def quote(symbol):
        """Fetches a quote for a given symbol, including price and other data

        Args:
            symbol (str): The stock symbol to be quoted. Not case sensitive.
        Returns:
            dict of str/int/float: JSON-like formatted quote containing info
                like price (latest/open/close), company name, quote time, and
                volume.
        Raises:
            StockifyAPIError: If the API returns a non-200 status code. Note that
                this will not catch all errors, since a bad response can be
                returned without a bad status code.
        """

        quote_url = f'https://api.iextrading.com/1.0/stock/{symbol}/quote'
        response = requests.get(quote_url)
        if response.status_code != 200:
            message = (f'API call failed with status code '
                       f'{response.status_code}: {json.loads(response.text)}')
            raise StockifyAPIError(message)
        else:
            decoded = json.loads(response.text)
            return decoded

    @staticmethod
    def quotes(symbol_list):
        """Calls the quote() method on a list of symbols, returning a quote dict

        Args:
            symbol_list (list of str): A simple list of symbols to retrieve
                quotes for.
        Returns:
            dict of quotes: Key:Value pairs of 'symbol':quote, where the quote
                is in turn a JSON-like dict of stock information. See documents
                on the .quote() method for more detail.
        """

        quote_list = [{symbol: Data.quote(symbol)} for symbol in symbol_list]
        return quote_list

    @staticmethod
    def price(symbol):
        """Quickly get the latest price, in USD, of a stock

        Args:
            symbol (str): The stock symbol whose price is to be returned. Not
                case sensitive.
        Returns:
            float: Last quoted price, in USD, of the stock queried.
        """

        return Data.quote(symbol)['latestPrice']

    @staticmethod
    def info(symbol):
        """Get basic information about a stock including name, sector, and price

        Args:
            symbol (str): The stock symbol whose information is to be returned.
                Not case sensitive.
        Returns:
            dict of str/int: JSON-like formatted dict containing the company
                name, sector, price, and primary exchange.
        """

        data = Data.quote(symbol)
        info_dict = {
            'companyName': data['companyName'],
            'sector': data['sector'],
            'latestPrice': ['latestPrice'],
            'primaryExchange': ['primaryExchange']
        }
        return info_dict


class HistoricalData(object):
    """Class for retrieving historical information about stocks and currencies

    Relies on the AlphaVantage API, which requires a free API key that must be
    supplied when the class is instantiated (see Stockify documentation). Once
    initialized data on stocks, fx rates, crypto rates, technical indicators,
    and sector performance can be retrieved, with various intervals.

    Args:
        api_key (str): A valid alphavantage API key.
    """

    BASE_URL = 'https://www.alphavantage.co/'
    # VALID_INTERVALS

    def __init__(self, api_key):

        self.api_key = api_key

    def _format_url(self, parameter_dict):
        """Private utility method to transform class methods into API urls

        API property:value pairs are passed to the function as a dict and are
        formatted into a string of key=value joined by &, which are then
        appended to the base url.

        Args:
            parameter_dict (dict of str): Key:value pairs of parameter names
                and values.
        Returns:
            str: A formatted url for the AlphaVantage API.
        """

        request_url = self.BASE_URL + 'query?'
        params = [f'{key}={value}' for key, value in parameter_dict.items()]
        params_string = '&'.join(params)
        request_url += params_string
        return request_url

    def _call_api(self, url):
        """Private utility method for making the API call and decoding response

        Args:
            url (str): A properly formatted url for the AlphaVantage API.
        Returns:
            dict: A JSON-like response dict containing the information returned
                by the API call.
        Raises:
            StockifyAPIError: If the API returns a non-200 status code. Note that
                this will not catch all errors, since a bad response can be
                returned without a bad status code.
        """

        response = requests.get(url)
        if response.status_code != 200:
            message = (f'API call failed with status code '
                       f'{response.status_code}: {json.loads(response.text)}')
            raise StockifyAPIError(message)
        else:
            decoded = json.loads(response.text)
            return decoded

    def stock(self, symbol, series_type, adjusted=False,
              datatype='json', interval='1min', compact=False):
        """Fetch time series data on a single stock (intraday or interday)

        Supports either intraday data fromr recent trading days, or data over
        the course of days, weeks, or months. Intraday typically contains data
        for the past 10-15 trading days, while day, week, and year contain up
        to 20 years of historical data.

        Data returned typically includes: timestamp, open, high, low, close,
        and volume.

        Args:
            symbol (str): The stock symbol to be fetched.
            series_type (str): Supports the following: intraday, day, week,
                month.
            adjusted (bool, optional): Determines if the closing price is
                adjusted or not. Defaults to False. Only applicable to day,
                week, and month series. Adjusted closing price is amended to
                include any distributions or corporate actions that occured
                before the next day's open.
            datatype (str, optional): Specifies whether data is returned in
                JSON-like or CSV-like format. Defaults to JSON.
            interval (str, optional): Specifies the resolution of the intraday
                series. Defaults to '1min'. Supported values are: 1, 5, 15, 30,
                and 60min. Only applicable to the intraday series type.
            compact (bool, optional): Determines whether the intraday series is
                truncated to 100 data points or contains all records available.
                Defaults to False. Only applicable tothe intraday series type.
        Returns:
            dict: JSON-like dict of timeseries stock data.
        Raises:
            StockifyError: If an unsupported series is not entered.
        """

        function_dict = {
            'intraday': 'TIME_SERIES_INTRADAY',
            'day': 'TIME_SERIES_DAILY',
            'week': 'TIME_SERIES_WEEKLY',
            'month': 'TIME_SERIES_MONTHLY'
        }

        request_params = {
            'symbol': symbol,
            'function': None,
            'apikey': self.api_key
        }

        if series_type not in function_dict.keys():
            raise StockifyError((f'Time series type {series_type} is not a '
                                 f'supported value'))

        if series_type == 'intraday':
            request_params['function'] = function_dict[series_type]
            request_params['outputsize'] = 'compact' if compact else 'full'
            request_params['datatype'] = datatype
            request_params['interval'] = interval
            request_url = self._format_url(request_params)
        else:
            request_params['function'] = (function_dict[series_type] +
                                          '_ADJUSTED' if adjusted
                                          else function_dict[series_type])
            request_params['datatype'] = datatype
            request_url = self._format_url(request_params)

        response = self._call_api(request_url)
        return response


    def fx_rate(self, from_currency, to_currency='USD', series_type='rate',
                datatype='json', interval='1min', compact=False):

        function_dict = {
            'rate': 'CURRENCY_EXCHANGE_RATE',
            'intraday': 'FX_INTRADAY',
            'day': 'FX_DAILY',
            'week': 'FX_WEEKLY',
            'month': 'FX_MONTHLY'
        }

        if series_type not in function_dict.keys():
            raise StockifyError((f'FX time series type {series_type} is not a '
                                 f'supported value'))

        request_params = {
            'function': function_dict[series_type],
            'apikey': self.api_key
        }

        if series_type == 'rate':
            request_params['from_currency'] = from_currency
            request_params['to_currency'] = to_currency
            request_url = self._format_url(request_params)
        else:
            request_params['from_symbol'] = from_currency
            request_params['to_symbol'] = to_currency
            request_params['outputsize'] = 'compact' if compact else 'full'
            request_params['datatype'] = datatype
            if series_type == 'intraday':
                request_params['interval'] = interval
            request_url = self._format_url(request_params)

        response = self._call_api(request_url)
        return response


    def crypto_rate(self, symbol, series_type, to_currency='USD'):

        function_dict = {
            'intraday': 'DIGITAL_CURRENCY_INTRADAY',
            'day': 'DIGITAL_CURRENCY_DAILY',
            'week': 'DIGITAL_CURRENCY_WEEKLY',
            'month': 'DIGITAL_CURRENCY_MONTHLY'
        }

        request_params = {
            'function': function_dict[series_type],
            'symbol': symbol,
            'market': to_currency,
            'apikey': self.api_key
        }

        request_url = self._format_url(request_params)
        response = self._call_api(request_url)
        return response

    def indicators(self, symbol, indicator, series_type, time_period,
                   interval='daily', datatype='json'):

        # For a full list of indicators supported see:
        # https://www.alphavantage.co/documentation/#technical-indicators
        request_params = {
            'symbol': symbol,
            'function': indicator,
            'series_type': series_type,
            'time_period': time_period,
            'interval': interval,
            'datatype': datatype,
            'apikey': self.api_key
        }

        request_url = self._format_url(request_params)
        response = self._call_api(request_url)
        return response

    def sector(self):

        request_params = {
            'function': 'SECTOR',
            'apikey': self.api_key
        }

        request_url = self._format_url(request_params)
        response = self._call_api(request_url)
        return response

    def batch_quotes(self, stock_list, datatype='json'):

        request_params = {
            'function': 'BATCH_STOCK_QUOTES',
            'datatype': datatype,
            'apikey': self.api_key
        }

        stock_list_string = ','.join(stock_list)
        request_params['symbols'] = stock_list_string
        request_url = self._format_url(request_params)
        response = self._call_api(request_url)
        return response
