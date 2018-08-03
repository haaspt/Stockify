import unittest
import Stockify


class PortfolioTest(unittest.TestCase):

    def test_holding(self):

        holding = Stockify.Holding('aapl')
        price = holding.get_price()
        expected_price = Stockify.Data.price('aapl')
        self.assertEqual(expected_price, price, ('Expected price did not match '
                                                 f'returned price: {price}'))
    
    def test_portfolio(self):

        portfolio = Stockify.Portfolio()
        symbol1 = 'aapl'
        symbol2 = 'v'
        portfolio.add_holding(symbol1)
        portfolio.add_holding(symbol2)
        self.assertEqual(2, len(portfolio.holdings))
        self.assertEqual('AAPL', portfolio['AAPL'].symbol)


if __name__ == '__main__':
    unittest.main()