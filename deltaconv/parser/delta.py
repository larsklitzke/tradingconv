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

from .parser import TradeHistoryParser


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
        transactions = []

        for t in transaction_list:
            row = TradeHistoryParser.Row(self._COLUMNS)

            values = {
                DeltaParser._COLUMN_DATE: t.datetime,
                DeltaParser._COLUMN_TYPE: t.type.upper(),
                DeltaParser._COLUMN_EXCHANGE: t.exchange,

                DeltaParser._COLUMN_BASE_AMOUNT: t.trading_pair[1].amount,
                DeltaParser._COLUMN_BASE_CURRENCY: self._CURRENCY_SYMBOL_MAPPING.get(
                    t.trading_pair[1].currency,
                    t.trading_pair[1].currency
                ),

                DeltaParser._COLUMN_QUOTA_AMOUNT: t.trading_pair[0].amount,
                DeltaParser._COLUMN_QUOTA_CURRENCY: self._CURRENCY_SYMBOL_MAPPING.get(
                    t.trading_pair[0].currency,
                    t.trading_pair[0].currency
                ),

                DeltaParser._COLUMN_FEE: t.fee.amount,
                DeltaParser._COLUMN_FEE_CURRENCY: self._CURRENCY_SYMBOL_MAPPING.get(
                    t.fee.currency,
                    t.fee.currency
                ),

                DeltaParser._COLUMN_COSTS: "",
                DeltaParser._COLUMN_COSTS_CURRENCY: "",
                DeltaParser._COLUMN_SYNC_HOLDING: 1,
                DeltaParser._COLUMN_SENT_RECEIVED_FROM: "",
                DeltaParser._COLUMN_SENT_TO: "",
                DeltaParser._COLUMN_NOTES: "",
            }

            row.update(values)

            transactions.append(row)

        self._write_transactions(transactions, csv_file)
        # writer.writerow(row.export())
