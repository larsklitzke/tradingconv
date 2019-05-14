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
import datetime

from deltaconv.transaction import CryptoList, Position, Fee, CryptoTransaction
from .parser import TradeHistoryParser, ParserOutdatedError


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
            if c not in self._COLUMNS:
                # otherwise, rise an exception that the parser is out of date
                raise ParserOutdatedError('The column {} is unknown. The parser has to be updated!'.format(c))

        transactions = []

        # parse all other rows
        for row in csv_content:
            row_ = TradeHistoryParser.Row(row=row, header=header)

            base, quota = _market_to_trading_pair(row_[self._COLUMN_MARKET])

            # old binance files had different way to store datetimes which will not be converted
            # by the xlsx module by default. Thus, we have to check this manually.
            if not isinstance(row_.get(self._COLUMN_DATE), datetime.datetime):
                row_[self._COLUMN_DATE] = datetime.datetime.strptime(row_[self._COLUMN_DATE], "%d.%m.%y %H:%M")

            # convert the row to a transaction
            transactions.append(CryptoTransaction(
                datetime=row_[self._COLUMN_DATE],
                trading_pair=(Position(amount=row_[self._COLUMN_TOTAL], currency=quota),
                              Position(amount=row_[self._COLUMN_COIN_AMOUNT], currency=base)),
                trading_type=row_[self._COLUMN_TYPE],
                price=row_[self._COLUMN_PRICE],
                fee=Fee(row_[self._COLUMN_FEE], row_[self._COLUMN_FEE_COIN]),
                exchange="Binance"
            ))

        return transactions

    def export(self, transaction_list, csv_file):
        """
        Write the list of `CryptoTransaction` into the given `csv_file`.

        Args:
            transaction_list (list[CryptoTransaction]): A list of `Transaction`s.
            csv_file (str): The path for the csv file.
        """

        transactions = []

        transaction_list = sorted(transaction_list, key=lambda t: t.datetime)

        for t in transaction_list:
            row = TradeHistoryParser.Row(self._COLUMNS)

            values = {
                self._COLUMN_DATE: t.datetime.strftime("%Y-%m-%d %H-%M-%S"),

                self._COLUMN_MARKET: "{}{}".format(t.trading_pair[1].currency.upper(),
                                                   t.trading_pair[0].currency),
                self._COLUMN_TYPE: t.type.upper(),
                self._COLUMN_PRICE: t.price,
                self._COLUMN_COIN_AMOUNT: t.trading_pair[1].amount,
                self._COLUMN_TOTAL: t.price * t.trading_pair[1].amount,
                self._COLUMN_FEE: t.fee.amount,
                self._COLUMN_FEE_COIN: t.fee.currency.upper()
            }

            row.update(values)

            transactions.append(values)

        self._write_transactions(transactions, "{}.xlsx".format(csv_file))


class BinanceCrawlerParser(TradeHistoryParser):
    """
    Parses csv files created by the binanceCrawler.

    """

    _COLUMN_TIME = 'time'
    _COLUMN_SIDE = 'side'
    _COLUMN_TRADEID = 'tradeId'
    _COLUMN_QUANTITY = 'qty'
    _COLUMN_FEE_COIN = 'feeAsset'
    _COLUMN_SYMBOL = 'symbol'
    _COLUMN_TOTAL_QUOTA = 'totalQuota'
    _COLUMN_REALPnl = 'realPnl'
    _COLUMN_QUOTE_ASSET = 'quoteAsset'
    _COLUMN_BASE_ASSET = 'baseAsset'
    _COLUMN_ID = 'id'
    _COLUMN_FEE = 'fee'
    _COLUMN_PRICE = 'price'
    _COLUMN_ACTIVE_BUY = 'activeBuy'

    _COLUMNS = [
        _COLUMN_TIME,
        _COLUMN_SIDE,
        _COLUMN_TRADEID,
        _COLUMN_QUANTITY,
        _COLUMN_FEE_COIN,
        _COLUMN_SYMBOL,
        _COLUMN_TOTAL_QUOTA,
        _COLUMN_REALPnl,
        _COLUMN_QUOTE_ASSET,
        _COLUMN_BASE_ASSET,
        _COLUMN_ID,
        _COLUMN_FEE,
        _COLUMN_PRICE,
        _COLUMN_ACTIVE_BUY,
    ]

    def parse(self, csv_file):

        csv_content = self._read_file(csv_file)

        # the first line is the header of the csv columns
        header = csv_content[0]
        del csv_content[0]

        missing_columns = list(set(self._COLUMNS) - set(header))
        if missing_columns:
            #
            #
            # # check if each entry in the header is in our list
            # for c in header:
            #     if c not in BinanceCrawlerParser._COLUMNS:
            # otherwise, rise an exception that the parser is out of date
            raise ParserOutdatedError(
                'The columns {} are unknown. The parser has to be updated!'.format(missing_columns))

        return [self.convert(row, header) for row in csv_content]

    @classmethod
    def convert(cls, row, header):
        """
        Converts the given `row` into a `Transaction`

        Args:
            row (list):     The row as a list of values
            header (list):  Description of each row entry

        Notes:
            The list lengths of row and header have to equal.

        Returns:
            CryptoTransaction:  The row converted into a CryptoTransaction

        """
        assert len(row) == len(header), 'Each column must have an entry in the header!'
        assert isinstance(row, list), 'The row should be a list'
        assert isinstance(header, list), 'The header should be list'

        row_ = TradeHistoryParser.Row(row=row, header=header)

        base, quota = row_[cls._COLUMN_BASE_ASSET], row_[cls._COLUMN_QUOTE_ASSET]

        return CryptoTransaction(
            datetime=datetime.datetime.utcfromtimestamp(row_[BinanceCrawlerParser._COLUMN_TIME] / 1000),
            trading_pair=(Position(amount=row_[BinanceCrawlerParser._COLUMN_TOTAL_QUOTA], currency=quota),
                          Position(amount=row_[BinanceCrawlerParser._COLUMN_QUANTITY], currency=base)),
            trading_type=row_[BinanceCrawlerParser._COLUMN_SIDE],
            price=row_[BinanceCrawlerParser._COLUMN_PRICE],
            fee=Fee(row_[BinanceCrawlerParser._COLUMN_FEE], row_[BinanceCrawlerParser._COLUMN_FEE_COIN]),
            exchange="Binance"
        )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
