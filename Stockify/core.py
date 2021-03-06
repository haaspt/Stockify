from datetime import datetime
import json
import csv
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
    Args:
        holdings (list of str, optional): A list of symbols to be added as
            holdings to the portfolio.
    """

    def __init__(self, holdings=None):
        self.holdings = {}
        if holdings:
            self.add_holdings(holdings)

    def add_holding(self, symbol):
        """Add a holding to the portfolio object.

        Args:
            symbol (str): The stock symbol to add as a holding
        """

        holding = Holding(symbol)
        self.holdings[symbol.upper()] = holding

    def add_holdings(self, symbol_list):
        """Add  a list of holdings passed in as a list of symbols.

        Args:
            symbol_list (list of str): A list of stock symbols to add as holdings
        """

        for symbol in symbol_list:
            self.add_holding(symbol)

    def get_value(self, symbol=None):
        """Gets the value of a single symbol or the entire portfolio.

        Args:
            symbol (str, optional): If specified the value of the holding is
                returned. If ommited the total value of the portfolio is returned.
        Returns:
            float: The USD value of the holding or sum of all holdings in the
                portfolio.
        """

        if symbol:
            return self.holdings[symbol.upper()].get_value()
        else:
            value = 0
            for holding in self.holdings.values():
                value += holding.get_value()
            return value

    def get_gains(self, symbol=None):

        if symbol:
            return self.holdings[symbol.upper()].get_gains()
        else:
            total_gains = 0
            day_gains = 0
            return_list = []
            for symbol, holding in self.holdings.items():
                holding_gains = holding.get_gains()
                day_gains += holding_gains['day']
                total_gains += holding_gains['total']
                return_list.append({symbol: holding_gains})
            total = {'total': {'day': day_gains, 'total': total_gains}}
            return_list.append(total)
            return return_list

    def get_prices(self):
        """Gets the current stock price of the holdings in the portfolio.

        Returns:
            list of dict{str:float}: A list of holding prices stored in a
                symbol: price dict.
        """

        return [{symbol: Data.price(symbol)} for symbol, _
                in self.holdings.items()]

    def remove(self, holding_symbol):
        """Remove a holding

        Args:
            holding_symbol (str): The symbol to be removed
        """

        self.holdings.pop(holding_symbol.upper())

    def to_file(self, filename, file_format='json'):
        """Save the current portfolio to disk as a JSON or CSV file

        Args:
            filename (str): The filename, including a file extension
            file_format (str, optional): The exported file format. Defaults to
                'json'. 'json' and 'csv' supported
        """
        date_format = '%Y-%m-%d'

        if not self.holdings:
            raise StockifyError('Cannot export a portfolio with no holdings')

        if file_format == 'json':
            export_data = []
            for symbol, holding in self.holdings.items():
                holding_data = {'symbol': symbol,
                                'lots': []}
                for lot in holding.lots:
                    lot_data = {'date': lot.date.strftime(date_format),
                                'cost_basis': lot.cost_basis,
                                'shares': lot.shares}
                    holding_data['lots'].append(lot_data)
                export_data.append(holding_data)
            with open(filename, 'w') as outfile:
                json.dump(export_data, outfile)
                print(f'Portfolio written to file: {filename}')
        elif file_format == 'csv':
            export_header = ['holding_symbol',
                             'lot_date',
                             'lot_cost_basis',
                             'lot_shares']
            export_rows = []
            for symbol, holding in self.holdings.items():
                for lot in holding.lots:
                    row = [symbol,
                           lot.date.strftime(date_format),
                           lot.cost_basis,
                           lot.shares]
                    export_rows.append(row)
            with open(filename, 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(export_header)
                writer.writerows(export_rows)
                print(f'Portfolio written to file: {filename}')
        else:
            raise StockifyError(f'{format} is not a supported file format.')

    def from_file(self, filename, file_format='json'):
        """Loads holdings and lots from disk.

        Holdings/lots that have already been added to the current portfolio
        will not be dropped or overwritten, so care should be taken when using
        this method to avoid duplicate data.

        Args:
            filename (str): The name of the file to load, including extension
            format (str, optional): The format of the file. Defaults to 'json'.
                'json' and 'csv' are supported.
        """

        if file_format == 'json':
            with open(filename, 'r') as importfile:
                import_data = json.load(importfile)
                holding_count = 0
                lot_count = 0
                for holding in import_data:
                    holding_count += 1
                    self.add_holding(holding['symbol'])
                    this_holding = self.__getitem__(holding['symbol'])
                    lot_data = holding['lots']
                    lot_list = [[lot['date'], lot['cost_basis'], lot['shares']]
                                for lot
                                in lot_data]
                    this_holding.add_lots(lot_list)
                    lot_count += len(holding['lots'])
                print((f'{holding_count} holdings and {lot_count} lots '
                       'loaded from file'))
        elif file_format == 'csv':
            with open(filename, 'r', newline='') as importfile:
                reader = csv.reader(importfile)
                next(reader) # Skip the header row
                holding_count = 0
                lot_count = 0
                for row in reader:
                    if len(row) > 4:
                        raise StockifyError(('Unexpected number of columns '
                                             'encountered in row.'))

                    if row[0] not in self.holdings.keys():
                        self.add_holding(row[0])
                        holding_count += 1
                    holding = self.holdings[row[0]]
                    holding.add_lot(row[1], float(row[2]), int(row[3]))
                    lot_count += 1
                print((f'{holding_count} holdings and {lot_count} lots '
                       'loaded from file'))
        else:
            raise StockifyError(f'{format} is not a supported file format.')

    def __len__(self):

        return len(self.holdings.keys())

    def __getitem__(self, item):

        return self.holdings[item.upper()]

    def __repr__(self):

        price_list = self.get_prices()
        return f'{json.dumps(price_list)}'


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

    def __init__(self, symbol):

        self.lots = []
        self.symbol = symbol.upper()
        self.total_shares = 0
        self.avg_cost_basis = 0.0

    def _calc_avg_cost_basis(self):

        avg_cost_basis = 0.0
        total_shares = 0
        number_of_lots = len(self.lots)
        if number_of_lots > 0:
            for lot in self.lots:
                lot_cost_basis = lot.cost_basis * lot.shares
                avg_cost_basis += lot_cost_basis
                total_shares += lot.shares
            avg_cost_basis = avg_cost_basis / total_shares
        return avg_cost_basis

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
        # Update holding totals
        self.total_shares += shares
        self.avg_cost_basis = self._calc_avg_cost_basis()

    def add_lots(self, lot_list):
        """Create multiple lots passed in as a list

        Args:
            lot_list (list of of lists): A list of lists, where each list item
                contains the three parameters needed to create a lot: date,
                cost basis, and shares, in that exact order.
        """

        for lot in lot_list:
            self.add_lot(lot[0], lot[1], lot[2])

    def get_value(self):
        """Calculates the total value of the holding, based on value of lots

        Returns:
            float: The USD sum of the values of the lots. Returns 0 if no lots
                have been added.
        """

        return self.total_shares * Data.price(self.symbol)

    def get_price(self):
        """The current market price of a single share of the holding.

        Returns:
            float: The current USD share price of the holding.
        """

        return Data.price(self.symbol)

    def get_gains(self):
        """The day and total gains of this holding since

        Returns:
            dict of {str: float}: The day and total gains for this holding
        """
        quote = Data.quote(self.symbol)
        current_value = round(quote['latestPrice'] * self.total_shares, 2)
        open_value = round(quote['open'] * self.total_shares, 2)
        initial_value = round(self.total_shares * self.avg_cost_basis, 2)
        day_gains = current_value - open_value
        total_gains = current_value - initial_value
        return {'day': day_gains, 'total': total_gains}

    def remove(self, lot_index):
        """Remove a lot by index

        Args:
            lot_index: The index number of the lot to be removed
        """

        del self.lots[lot_index]

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
        self.initial_value = round(shares * cost_basis, 2)

    @property
    def total_gains(self):
        """Total returns of the lot, in USD, since original purchase.

        Returns:
            float: current market value - initial value
        """
        return round(self.market_value - self.initial_value, 2)

    @property
    def day_gains(self):
        """The increase in value of this holding in the current or previous day

        Returns:
            float: Price in USD of current market value - value at open
        """
        open_price = Data.quote(self.symbol)['open']
        current_price = Data.price(self.symbol)
        return round((current_price * self.shares) - (open_price * self.shares),
                     2)

    @property
    def market_value(self):
        """Returns the USD value of the lot (shares * current price)

        Returns:
            float: the value of the lot multipled by shares
        """
        return round(self.shares * Data.price(self.symbol), 2)

    def __lt__(self, other):

        return self.date < other.date

    def __repr__(self):

        return (f'{self.date.strftime(self._dateformat)} :: {self.shares} '
                f'shares {self.symbol} @ {self.cost_basis}')
        