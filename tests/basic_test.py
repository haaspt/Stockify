import unittest
import Stockify

from credentials import api_key

class APITest(unittest.TestCase):

    def test_historical(self):
        api = Stockify.StockifyData(api_key)
        result = api.historical('aapl', 'intraday')
        self.assertNotIn('Error Message', result.keys(), "API call returned an error.")

    def test_fx_rate(self):
        api = Stockify.StockifyData(api_key)
        result = api.fx_rate('eur', series_type='intraday')
        self.assertNotIn('Error Message', result.keys(), "API call returned an error.")

if __name__ == '__main__':
    unittest.main()