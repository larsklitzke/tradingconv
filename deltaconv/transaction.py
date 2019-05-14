# -*- coding: utf-8 -*-

# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import json
import urllib.request


class Currency(object):
    """
    This is a generic class for representing a currency,
    """

    @property
    def symbol(self):
        """
        The symbol name of the coin which is a short form of the coin name.

        Returns:
            The symbol name of the coin

        """
        return self.__symbol

    @property
    def name(self):
        """
        The name of the coin.

        Returns:
            The full name of the coin

        """
        return self.__name

    def __init__(self, name, symbol, **kwargs):
        super().__init__()

        self.__name = name
        self.__symbol = symbol

    def __str__(self):
        return self.__symbol


class CryptoCurrency(Currency):
    """
    This is a special type of currency. In order to initialize a CrpytoCurrency, use can use the `CryptoList` which will
    query coinmarketcap in order to retrieve a list of all available cryptocurrency coins/tokens.
    """

    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)

        self.__id = id

    @property
    def id(self):
        """
        The id of the coin given by the coinmarketcap API.

        Returns:
            The id of the coin
        """
        return self.__id


class CryptoList(list):
    """
    This class is a list of all available crypto coins with each coin represented by its symbol name.

    On initialization, the list of crypto coins will be queried using the APIv2 of coinmarketcap.
    """

    _COINTMARKETCAP_QUERY_LISTING = 'https://api.coinmarketcap.com/v2/listings/'

    def __query_coinmarketcap(self):

        with urllib.request.urlopen(self._COINTMARKETCAP_QUERY_LISTING) as response:
            data = json.loads(response.read().decode())

            if data:
                return data['data']

    def __init__(self):

        super().__init__()

        self._coin_map = {}

        for entry in self.__query_coinmarketcap():
            c = CryptoCurrency(**entry)

            self.append(c)

            self._coin_map[c.symbol] = c

    def find_symbol(self, symbol):

        if symbol not in self._coin_map:

            if symbol == "IOTA":
                return self._coin_map["MIOTA"]

        else:
            return self._coin_map[symbol]


class Position(object):
    """ A position represents a trade amount and its currency. """

    def __init__(self, amount, currency):
        self.__amount = amount
        self.__currency = currency

    @property
    def amount(self):
        """
        The position amount

        Returns:
            float: The position amount

        """
        return self.__amount

    @property
    def currency(self):
        """
        The position currency.

        Returns:
            str: The name of the currency.

        """
        return self.__currency


class Fee(Position):
    """ The fee of a transaction """
    pass


class Transaction(object):
    """
    Generic type of a transaction
    """

    @property
    def datetime(self):
        """
        The date and time of the transaction

        Returns:
            datetime.datetime: The datetime of the transaction

        """
        return self.__datetime

    @property
    def trading_pair(self):
        """
        A pair of currencies representing the trading direction

        Returns:
            tuple[Position, Position]: A tuple with two positions

        """
        return self.__trading_pairs

    @property
    def type(self):
        """
        The trading type

        Returns:
            str: The type of trading
        """
        return self.__trading_type

    @property
    def price(self):
        """
        The price per coin.

        Returns:
            float: The price of a coin.

        """
        return self.__price

    @property
    def fee(self):
        """
        The trading fee

        Returns:
            Fee: The trading fee

        """
        return self.__fee

    def __init__(self, datetime, trading_pair, trading_type, price, fee):
        """

        Args:
            datetime (datetime):                        The trading time
            trading_pair (tuple[Position, Position]):   A tuple of the source and target trading currency
            trading_type (str):                         The type of the trade
            price (float):                              The price per coin
            fee (Fee):                                  Amount of trading fee
        """

        super().__init__()

        self.__datetime = datetime
        self.__trading_pairs = trading_pair
        self.__trading_type = trading_type
        self.__price = price

        assert isinstance(fee, Fee), 'The fee has to be of type Fee.'
        self.__fee = fee

    def __repr__(self):
        return ", ".join([self.datetime,
                          self.trading_pair[0],
                          self.trading_pair[1],
                          str(self.price),
                          str(self.fee.amount),
                          self.fee.currency])


class CryptoTransaction(Transaction):
    """
    A transaction which took place on a certain exchange, e.g. Binance.
    """

    def __init__(self, exchange, **kwargs):
        """

        Args:
            exchange: The exchange on which the transaction took place

        Keyword Args:
            Will be passed to the `Transaction` parent class.

        """
        super().__init__(**kwargs)

        self._exchange = exchange

    @property
    def exchange(self):
        """
        The name of the exchange.

        Returns:
            str: The name of the exchange

        """
        return self._exchange
