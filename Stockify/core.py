import requests
import json

class StockifyError(Exception):
    pass

class APICaller(object):

    BASE_URL = 'https://www.alphavantage.co/'
    # VALID_INTERVALS
    
    def __init__(self, api_key):

        self.api_key = api_key

    def _format_url(self, function_name, symbol, interval, outputsize, datatype):
        # TODO: Rewrite to accomodate various parameters
        request_url = f'{self.BASE_URL}query?function={function_name}&symbol={symbol}&interval={interval}&outputsize={outputsize}&datatype={datatype}&apikey={self.api_key}'
        return request_url

    def _call_url(self, url):

        response = requests.get(url)
        if response.status_code is not 200:
            message = f'API call failed with status code {response.status_code}: {json.loads(response.text)}'
            raise StockifyError(message)
        else:
            decoded = json.loads(response.text)
            return decoded

    def get_time_series(self, symbol, series_type, adjusted=False, datatype='json', interval='1m', compact=False):

        function_dict = {
            'intraday': 'TIME_SERIES_INTRADAY',
            'day': 'TIME_SERIES_DAILY',
            'week': 'TIME_SERIES_WEEKLY',
            'month': 'TIME_SERIES_MONTHLY'
        }

        if series_type not in function_dict.keys():
            raise StockifyError(f'Time series type {series_type} is not a supported value')
        
        if series_type == 'intraday':
            outputsize = 'compact' if compact else 'full'
            request_url = self._format_url(function_dict[series_type], symbol, interval, outputsize, datatype)
        else:
            function_name = function_dict[series_type] + '_ADJUSTED' if adjusted else function_dict[series_type]
            # TODO: fix the URL formatter
            # request_url = self._format_url(function_name, symbol, datatype)
        
        response = self._call_url(request_url)
        return response

    def get_fx_rates(self, from_currency, to_currency, series_type, datatype='json', interval='1m', compact=False):
        pass

    def get_crypto_rates(self, from_currency, to_currency, series_type):
        # Currency lists:
        # Physical: https://www.alphavantage.co/physical_currency_list/
        # Crypto: https://www.alphavantage.co/digital_currency_list/
        pass

    def get_technical_indicators(self):
        pass

    def get_sector_performace(self):
        pass    

    def get_batch_quotes(self):
        pass