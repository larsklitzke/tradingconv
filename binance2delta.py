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
import argparse
import csv
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


class TradeHistoryParser(object):
    class Row(dict):
        """
        Represents a row in a csv file for reading and writing

        """

        def __init__(self, header, row=None):
            """
            Initialize a Row object with a row of a csv file and the header of the row

            Args:
                row:        The row of the csv file (optional)
                header:     A header with the names of the columns
            """

            super().__init__()

            self.__header = header

            if row:
                for idx, column in enumerate(row):

                    # try to convert column value to float
                    try:
                        column = float(column.replace(',', '.'))
                    except ValueError:
                        # ok this failed - just use the value
                        pass

                    self[header[idx]] = column

        def export(self):
            """
            Export the row. Can be used to write a row into a csv file

            Returns:
                A list of columns in the same order as the given header
            """
            row = []

            for column in self.__header:
                row.append(self.get(column))

            return row

    def parse(self, csv_file):
        """
        Parses the given csv_file

        Args:
            csv_file:

        Returns:
            A list of `Transaction`s

        """
        raise NotImplementedError('You have to implement the parser() function.')

    def export(self, transaction_list, csv_file):
        """
        Exports the list of transactions as a CSV file with the binance format

        Args:
            transaction_list: A list of transactions
            csv_file: The name of the file to export the transactions into

        Notes:
            If the `csv_file` already exists, the content will be overwritten!

        """
        raise NotImplementedError('You have to implement the export() function.')

    def _read_csv_file(self, csv_file):
        """
        Get the content of the given `csv_file` as list of rows

        Args:
            csv_file: The csv file to read

        Returns:
            The content of the csv file as a list of rows
        """

        with open(csv_file, 'r') as file_:
            return list(csv.reader(file_, **self._cfg))

    def __init__(self, **kwargs):

        super().__init__()

        self._cfg = kwargs


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

        csv_content = self._read_csv_file(csv_file)

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

            base, quota = self._market_to_trading_pair(row_[self._COLUMN_MARKET])

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

    def _market_to_trading_pair(self, market):
        """
        This function will convert the market column into a trading pair

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
            other_symbol = market.replace(c.symbol, "")

            if coins.find_symbol(other_symbol):
                # market is valid
                return __get_currencies(other_symbol, c.symbol)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class DeltaParser(TradeHistoryParser):

    def parse(self, csv_file):
        super().parse(csv_file=csv_file)

    # This field contains the date and time of the transaction, including the timezone.
    _COLUMN_DATE = "Date"

    # The type of the transaction.
    _COLUMN_TYPE = "Type"

    # The exchange where the trade (or deposit/withdraw) was made. Optional for trades.
    _COLUMN_EXCHANGE = "Exchange"

    # The amount you were trading or transferring (excluding fees)
    _COLUMN_BASE_AMOUNT = "Base Amount"

    # The currency you were trading or transferring
    _COLUMN_BASE_CURRENCY = "Base currency"

    # For trades, the amount you were trading it for (excluding fees).
    _COLUMN_QUOTA_AMOUNT = "Quote amount"

    # The trade currency
    _COLUMN_QUOTA_CURRENCY = "Quote currency"

    # The fee that was paid on the trade or transfer
    _COLUMN_FEE = "Fee"

    # The currency of the fee
    _COLUMN_FEE_CURRENCY = "Fee currency"

    # Optional, used for an ICO, we'll take this amount as money invested
    _COLUMN_COSTS = "Costs / Proceeds"

    # Optional, used for an ICO, the currency of the amount invested
    _COLUMN_COSTS_CURRENCY = "Costs / Proceeds currency"

    # Optional, for trades. When set to 1, the quote will be added to or deducted from your holdings
    # (depending if it's a SELL or BUY). It's recommended but it can result in a negative balance if you manually
    # entered corresponding trades/transfers.
    _COLUMN_SYNC_HOLDING = "Sync Holdings"

    # In case of an ICO, this field should be 'ICO', otherwise it's only used for transfers.
    # You can specify the name of an exchange, 'MY_WALLET', 'OTHER_WALLET', 'BANK', 'AIRDROP', 'MINING', 'FORK', ...
    _COLUMN_SENT_RECEIVED_FROM = "Sent / Received from"

    # Only used for transfers. You can specify the name of an exchange, 'MY_WALLET', 'OTHER_WALLET', 'BANK' or 'OTHER'
    _COLUMN_SENT_TO = "Sent to"

    # Your notes you want to keep for this transaction (optional)
    _COLUMN_NOTES = "Notes"

    _COLUMNS = [
        _COLUMN_DATE,
        _COLUMN_TYPE,
        _COLUMN_EXCHANGE,
        _COLUMN_BASE_AMOUNT,
        _COLUMN_BASE_CURRENCY,
        _COLUMN_QUOTA_AMOUNT,
        _COLUMN_QUOTA_CURRENCY,
        _COLUMN_FEE,
        _COLUMN_FEE_CURRENCY,
        _COLUMN_COSTS,
        _COLUMN_COSTS_CURRENCY,
        _COLUMN_SYNC_HOLDING,
        _COLUMN_SENT_RECEIVED_FROM,
        _COLUMN_SENT_TO,
        _COLUMN_NOTES
    ]

    # A list of currency symbol mappings
    _CURRENCY_SYMBOL_MAPPING = {
        "IOTA": "MIOTA"
    }

    def export(self, transaction_list, csv_file):
        with open(csv_file, 'a') as file_:
            writer = csv.writer(file_, **self._cfg)

            # write the header
            writer.writerow(self._COLUMNS)

            for t in transaction_list:
                row = TradeHistoryParser.Row(self._COLUMNS)

                row[DeltaParser._COLUMN_DATE] = t.datetime
                row[DeltaParser._COLUMN_TYPE] = t.type.upper()
                row[DeltaParser._COLUMN_EXCHANGE] = ""

                row[DeltaParser._COLUMN_BASE_AMOUNT] = t.trading_pair[1].amount
                row[DeltaParser._COLUMN_BASE_CURRENCY] = self._CURRENCY_SYMBOL_MAPPING.get(
                    t.trading_pair[1].currency,
                    t.trading_pair[1].currency
                )

                row[DeltaParser._COLUMN_QUOTA_AMOUNT] = t.trading_pair[0].amount
                row[DeltaParser._COLUMN_QUOTA_CURRENCY] = self._CURRENCY_SYMBOL_MAPPING.get(
                    t.trading_pair[0].currency,
                    t.trading_pair[0].currency
                )

                row[DeltaParser._COLUMN_FEE] = t.fee.amount
                row[DeltaParser._COLUMN_FEE_CURRENCY] = self._CURRENCY_SYMBOL_MAPPING.get(
                    t.fee.currency,
                    t.fee.currency
                )

                row[DeltaParser._COLUMN_COSTS] = ""
                row[DeltaParser._COLUMN_COSTS_CURRENCY] = ""
                row[DeltaParser._COLUMN_SYNC_HOLDING] = 1
                row[DeltaParser._COLUMN_SENT_RECEIVED_FROM] = ""
                row[DeltaParser._COLUMN_SENT_TO] = ""
                row[DeltaParser._COLUMN_NOTES] = ""

                writer.writerow(row.export())


_PARSER = {
    'binance': {
        'parser': BinanceParser,
        'config': {
            'delimiter': ",",
        }
    },

    'delta': {
        'parser': DeltaParser,
        'config': {
            'delimiter': ',',
        }
    }
}


def parse_arguments():
    """Parses the arguments the user passed to this script """

    # parse parameter
    arg_parser = argparse.ArgumentParser(description='''
            This tool parses a CSV file formatted in Binance format to a CSV file with the Delta format in order to 
            import Binance transactions into the Delta application.
            ''')

    arg_parser.add_argument('--file', help="The csv file", required=True)

    arg_parser.add_argument('--format', help="The format of the input csv file", required=True, choices=_PARSER.keys())

    arg_parser.add_argument('--output', help="The name of the CSV file with delta format", required=False, default=None)

    return arg_parser.parse_args()


def init_parser(source_format):
    """ Initialize a Parser pased on the given source format

    Args:
        source_format: The format of the source file, e.g. binance.
    """

    choice = _PARSER[source_format]

    return choice['parser'](**choice['config'])


if __name__ == "__main__":
    arguments = parse_arguments()

    parser = init_parser(arguments.format)

    transaction_list = parser.parse(arguments.file)

    delta_parser = init_parser("delta")

    delta_parser.export(transaction_list=transaction_list, csv_file=arguments.output)
