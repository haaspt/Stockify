import requests
import json

class StockifyError(Exception):
    pass

class StockifyData(object):

    BASE_URL = 'https://www.alphavantage.co/'
    # VALID_INTERVALS
    
    def __init__(self, api_key):

        self.api_key = api_key

    def _format_url(self, parameter_dict):
        request_url = self.BASE_URL + 'query?'
        params = [f'{key}={value}' for key, value in parameter_dict.items()]
        params_string = '&'.join(params)
        request_url += params_string
        return request_url

    def _call_api(self, url):

        response = requests.get(url)
        if response.status_code != 200:
            message = f'API call failed with status code {response.status_code}: {json.loads(response.text)}'
            raise StockifyError(message)
        else:
            decoded = json.loads(response.text)
            return decoded

    @staticmethod
    def quote(symbol):
        quote_url = f'https://api.iextrading.com/1.0/stock/{symbol}/quote'
        response = requests.get(quote_url)
        if response.status_code != 200:
            message = f'API call failed with status code {response.status_code}: {json.loads(response.text)}'
            raise StockifyError(message)
        else:
            decoded = json.loads(response.text)
            return decoded

    def historical(self, symbol, series_type, adjusted=False, datatype='json', interval='1min', compact=False):

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
            raise StockifyError(f'Time series type {series_type} is not a supported value')
        
        if series_type == 'intraday':
            request_params['function'] = function_dict[series_type]
            request_params['outputsize'] = 'compact' if compact else 'full'
            request_params['datatype'] = datatype
            request_params['interval'] = interval
            request_url = self._format_url(request_params)
        else:
            request_params['function'] = function_dict[series_type] + '_ADJUSTED' if adjusted else function_dict[series_type]
            request_params['datatype'] = datatype
            request_url = self._format_url(request_params)
        
        response = self._call_api(request_url)
        return response


    def fx_rate(self, from_currency, to_currency='USD', series_type='rate', datatype='json', interval='1min', compact=False):
        
        function_dict = {
            'rate': 'CURRENCY_EXCHANGE_RATE',
            'intraday': 'FX_INTRADAY',
            'day': 'FX_DAILY',
            'week': 'FX_WEEKLY',
            'month': 'FX_MONTHLY' 
        }

        if series_type not in function_dict.keys():
            raise StockifyError(f'FX time series type {series_type} is not a supported value')

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

    def indicators(self, symbol, indicator, series_type, time_period, interval='daily', datatype='json'):
        
        # For a full list of indicators supported see: https://www.alphavantage.co/documentation/#technical-indicators
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
