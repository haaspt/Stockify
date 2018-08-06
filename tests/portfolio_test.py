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
        self.assertEqual(2, len(portfolio))
        self.assertEqual('AAPL', portfolio['AAPL'].symbol)
        portfolio.add_holdings(['ms', 'fb'])
        self.assertEqual(4, len(portfolio))

        my_holdings = ['aapl', 'v', 'ms']
        portfolio_with_holdings = Stockify.Portfolio(my_holdings)
        number_of_holdings = len(portfolio_with_holdings)
        self.assertEqual(4, number_of_holdings)
        # Value returns 0.0 because no lots have been added
        self.assertEqual(0.0, portfolio_with_holdings.get_value())
        self.assertEqual(4, len(portfolio_with_holdings.get_prices()))


if __name__ == '__main__':
    unittest.main()
