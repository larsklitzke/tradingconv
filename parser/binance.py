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
from parser.parser import TradeHistoryParser, ParserOutdatedError
from transaction import CryptoList, Transaction, Position, Fee


def _market_to_trading_pair(market):
    """
    This function will convert the market column of the binance file into a trading pair

    Args:
        market: A value of the market column of the csv file

    Returns:
        A tuple with two entries representing the trading pair or None if the pair is unknown

    """

    # at first, get a list of all available cryptocoins
    coins = CryptoList()

    def __get_currencies(other_symbol, symbol):
        if market.startswith(symbol):
            # start of the string
            return c, coins.find_symbol(other_symbol)
        elif market.endswith(symbol):
            # end of the string
            return coins.find_symbol(other_symbol), c

    # now check if any of the coins symbol name is in the market
    for c in coins:
        second_symbol = market.replace(c.symbol, "")

        if coins.find_symbol(second_symbol):
            # market is valid
            return __get_currencies(second_symbol, c.symbol)


class BinanceParser(TradeHistoryParser):
    """
    Parses csv files of the Binance exchange platform.

    """

    _COLUMN_DATE = "Date(UTC)"

    _COLUMN_TYPE = "Type"

    _COLUMN_MARKET = "Market"

    _COLUMN_PRICE = "Price"

    _COLUMN_FEE_COIN = "Fee Coin"

    _ORDER_SELL = "Sell"

    _ORDER_BUY = "Buy"

    _COLUMN_TOTAL = "Total"

    _COLUMN_FEE = "Fee"

    _COLUMN_COIN_AMOUNT = "Amount"

    _COLUMNS = [
        _COLUMN_DATE,
        _COLUMN_MARKET,
        _COLUMN_TYPE,
        _COLUMN_PRICE,
        _COLUMN_COIN_AMOUNT,
        _COLUMN_TOTAL,
        _COLUMN_FEE,
        _COLUMN_FEE_COIN
    ]

    def parse(self, csv_file):

        csv_content = self._read_file(csv_file)

        # the first line is the header of the csv columns
        header = csv_content[0]
        del csv_content[0]

        # check if each entry in the header is in our list
        for c in header:
            if c not in BinanceParser._COLUMNS:
                # otherwise, rise an exception that the parser is out of date
                raise ParserOutdatedError('The column {} is unknown. The parser has to be updated!'.format(c))

        transactions = []

        # parse all other rows
        for row in csv_content:
            row_ = TradeHistoryParser.Row(row=row, header=header)

            base, quota = _market_to_trading_pair(row_[self._COLUMN_MARKET])

            # convert the row to a transaction
            transactions.append(Transaction(
                datetime=row_[self._COLUMN_DATE],
                trading_pair=(Position(amount=row_[self._COLUMN_TOTAL], currency=quota),
                              Position(amount=row_[self._COLUMN_COIN_AMOUNT], currency=base)),
                trading_type=row_[self._COLUMN_TYPE],
                price=row_[self._COLUMN_PRICE],
                fee=Fee(row_[self._COLUMN_FEE], row_[self._COLUMN_FEE_COIN])
            ))

        return transactions

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
