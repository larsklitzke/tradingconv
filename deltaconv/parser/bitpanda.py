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
from deltaconv.parser.parser import TradeHistoryParser, ParserOutdatedError
from deltaconv.transaction import CryptoTransaction, Position, Fee


class BitpandaParser(TradeHistoryParser):
    """
    Parses csv files of the Bitpanda exchange platform.

    """

    _COLUMN_ID = "ID"

    _COLUMN_DATE = "Created at"

    _COLUMN_TYPE = "Type"

    _COLUMN_DIRECTION = "In/Out"

    _COLUMN_FIAT = "Fiat Currency"

    _COLUMN_FIAT_AMOUNT = "Amount Fiat"

    _COLUMN_CRYPTO = "Cryptocoin"

    _COLUMN_CRYPTO_AMOUNT = "Amount Cryptocoin"

    _COLUMN_STATUS = "Status"

    _COLUMNS = [
        _COLUMN_ID,
        _COLUMN_DATE,
        _COLUMN_TYPE,
        _COLUMN_DIRECTION,
        _COLUMN_FIAT,
        _COLUMN_FIAT_AMOUNT,
        _COLUMN_CRYPTO,
        _COLUMN_CRYPTO_AMOUNT,
        _COLUMN_STATUS
    ]

    def parse(self, csv_file):

        csv_content = self._read_file(csv_file)

        # the first line is a disclaimer and the second line is the title with the account email address
        del csv_content[0:2]

        # the third line is the header
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

            if row_[self._COLUMN_TYPE] in ['buy', 'sell']:
                # only process buy and sells

                transactions.append(CryptoTransaction(
                    datetime=row_[self._COLUMN_DATE],
                    trading_pair=(Position(amount=row_[self._COLUMN_FIAT_AMOUNT], currency=row_[self._COLUMN_FIAT]),
                                  Position(amount=row_[self._COLUMN_CRYPTO_AMOUNT],
                                           currency=row_[self._COLUMN_CRYPTO])),
                    trading_type=row_[self._COLUMN_TYPE],

                    # calculate the price based on the amount of fiat used to buy a certain amount of cryptocoins
                    price=row_[self._COLUMN_FIAT_AMOUNT] / row_[self._COLUMN_CRYPTO_AMOUNT],

                    # we actually cannot calculate the fee using the data provided by bitpanda
                    fee=Fee(0, row_[self._COLUMN_FIAT]),
                    exchange="Bitpanda"
                ))

        return transactions
