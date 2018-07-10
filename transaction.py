# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017 by Lars Klitzke, Lars.Klitzke@gmail.com
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior
#      written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import json
import urllib.request


class ParserOutdatedError(RuntimeError):
    """ Raise this exception if a TradingParser is out of date.

    """
    pass


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
        return self.__amount

    @property
    def currency(self):
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
            The datetime of the transaction

        """
        return self.__datetime

    @property
    def trading_pair(self):
        """
        A pair of currencies representing the trading direction

        Returns:
            A tuple with two element which are

        """
        return self.__trading_pairs

    @property
    def type(self):
        """
        The trading type

        Returns:
            The type of trading
        """
        return self.__trading_type

    @property
    def price(self):
        return self.__price

    @property
    def fee(self):
        return self.__fee

    def __init__(self, datetime, trading_pair, trading_type, price, fee):
        """

        Args:
            datetime:           The trading time
            trading_pair:       A tuple of the source and target trading currency
            trading_type:       The type of the trade
            price:              The price per coin
            fee:                Amount of trading fee of type `Fee`
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
