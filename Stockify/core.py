from datetime import date, datetime
from .api import Data
from .errors import StockifyError


class Portfolio(object):
    """An object to store a stock portfolio and calculate its value

    The porfolio is used to store Holdings, which are in turn comprised of Lots.
    Once a holding is added using the `.add_holding()` method it can be accessed
    using subscript notation: 
        # Add
        `portfolio.add_holding('aapl')`
        # Access
        `portfolio['aapl']`
    """

    holdings = {}
    
    
    def add_holding(self, symbol):
        """Add a holding to the portfolio object.

        Args:
            symbol (str): The stock symbol to add as a holding
        """

        holding = Holding(symbol)
        self.holdings[symbol.upper()] = holding

    def get_value(self, symbol=None):
        """Gets the value of a single symbol or the entire portfolio.

        Args:
            symbol (str, optional): If specified the value of the holding is
                returned. If ommited the total value of the portfolio is returned.
        Returns:
            float: The USD value of the holding or sum of all holdings in the
                portfolio.
        Raises:
            StockifyError: If the symbol of a holding not in the portfolio is
                entered.
        """

        if symbol:
            if symbol not in self.holdings.keys():
                raise StockifyError(f'Symbol {symbol.upper()} not in holdings.')
            return self.holdings[symbol.upper()].get_value()
        else:
            value = 0
            for holding in self.holdings.values():
                value += holding.get_value()
            return value

    def get_prices(self):
        """Gets the current stock price of the holdings in the portfolio.

        Returns:
            list of dict{str:float}: A list of holding prices stored in a
                symbol: price dict.
        """

        return [{symbol: Data.price(symbol)} for symbol in self.holdings.keys()]

    def __getitem__(self, item):

        return self.holdings[item.upper()]

    def __repr__(self):

        return f'{self.get_prices}'


class Holding(object):
    """An object to store a holding, an ownership interest in a stock

    A holding is ownership of a given stock, made up of one or more lots.
    Holdings are initialized and then lots are added with the `.add_lot()`
    method.

    The `.get_price()` method returns the current share price of the holding.

    The `.get_value()` method returns the total value of the lots comprising
    the holding.

    Args:
        symbol (str): The stock symbol of the holding.

    Attributes:
        lots (list of Lots): A list of the lots comprising this holding. Added
            via `.add_lot()` method.
    """

    lots = []
    
    def __init__(self, symbol):

        self.symbol = symbol.upper()

    def add_lot(self, date, cost_basis, shares):
        """Creates a Lot object and appends it to the self.lots attribute

        Args:
            date (str): The date of the lot in the following format: 'YYYY-MM-DD'
            cost_basis (float): the cost-per-share of the stock, net of fees, etc.
            shares (float): the number of shares purchased
        """

        lot = Lot(self.symbol, date, cost_basis, shares)
        self.lots.append(lot)
        self.lots.sort()

    def get_value(self):
        """Calculates the total value of the holding, based on value of lots

        Returns:
            float: The USD sum of the values of the lots. Returns 0 if no lots
                have been added.
        """

        value = 0.0
        for lot in self.lots:
            value += lot.get_value()
        return value

    def get_price(self):
        """The current market price of a single share of the holding.

        Return:
            float: the current USD share price of the holding.
        """

        return Data.price(self.symbol)

    def __getitem__(self, item):

        return self.lots[item]

    def __len__(self):

        return len(self.lots)

    def __repr__(self):

        return f'Holding: {self.symbol}; Lots: {self.lots}'


class Lot(object):
    """An object to store a lot, a group of shares purchased in a transaction

    Lots store the basic information about cost basis and shares that allow for
    total value of a holding to be calculated.

    Args:
        symbol (str): the stock symbol of the lot
        date (str): a date in the following format: 'YYYY-MM-DD'
        cost_basis (float): the cost-per-share of the stock, net of fees, etc.
        shares (float): the number of shares purchased
    """

    _dateformat = '%Y-%m-%d'
    
    def __init__(self, symbol, date, cost_basis, shares):

        self.symbol = symbol.upper()
        self.date = datetime.strptime(date, self._dateformat).date()
        self.cost_basis = cost_basis
        self.shares = shares
    
    def get_value(self):
        """Returns the USD value of the lot (shares * current price)

        Returns:
            float: the value of the lot multipled by shares
        """
        return self.shares * Data.price(self.symbol)

    def __lt__(self, other):

        return self.date < other.date

    def __repr__(self):

        return (f'{self.date.strftime(self._dateformat)} :: {self.shares} '
                f'shares {self.symbol} @ {self.cost_basis}')
        