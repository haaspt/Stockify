import unittest
import os
import Stockify

try:
    api_key = os.environ['STOCKIFY_API_KEY']
except KeyError:
    from credentials import api_key

class APITest(unittest.TestCase):

    def test_historical(self):
        api = Stockify.HistoricalData(api_key)
        result = api.historical('aapl', 'intraday')
        self.assertNotIn('Error Message', result.keys(), "API call returned an error.")

    def test_fx_rate(self):
        api = Stockify.HistoricalData(api_key)
        result = api.fx_rate('eur', series_type='intraday')
        self.assertNotIn('Error Message', result.keys(), "API call returned an error.")

if __name__ == '__main__':
    unittest.main()