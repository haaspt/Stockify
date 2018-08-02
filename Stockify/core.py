from datetime import date
from .api import Data
from .errors import StockifyError


class Portfolio(object):
    
    def __init__(self):

        self.holdings = {}
    
    def add_holding(self, symbol):

        holding = Holding(symbol)
        self.holdings[symbol.upper()] = holding

    def get_value(self, symbol=None):

        if symbol:
            if symbol not in self.holdings.keys():
                raise StockifyError(f'Symbol {symbol.upper()} not in holdings.')
            return self.holdings[symbol.upper()].get_value()
        else:
            value = 0
            for holding in self.holdings.values():
                value += holding.get_value()
            return value


class Holding(object):
    
    def __init__(self, symbol):

        self.lots = []
        self.symbol = symbol.upper()

    def add_lot(self, date, cost_basis, shares):

        lot = Lot(self.symbol, date, cost_basis, shares)
        self.lots.append(lot)

    def get_value(self):

        value = 0
        for lot in self.lots:
            value += lot.get_value()
        return value


class Lot(object):
    
    def __init__(self, symbol, date, cost_basis, shares):

        self.symbol = symbol.upper()
        self.date = date
        self.cost_basis = cost_basis
        self.shares = shares
    
    def get_value(self):

        return self.shares * Data.price(self.symbol)
        