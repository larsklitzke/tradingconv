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


import csv
import datetime
import os


class ParserOutdatedError(RuntimeError):
    """ Raise this exception if a TradingParser is out of date.

    """
    pass


class TradeHistoryParser(object):
    class Row(dict):
        """
        Represents a row in a file for reading and writing

        """

        def __init__(self, header, row=None):
            """
            Initialize a Row object with a row of tabular calculation file and the header of the row

            Args:
                row:        The row of the csv file as a list of values (optional)
                header:     A header with the names of the columns
            """

            super().__init__()

            self.__header = header

            if row:
                for idx, column in enumerate(row):
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

    def _read_file(self, file):
        """
        Get the content of the given `file` as list of rows

        Args:
            file: The file to read (either xl(s)x or csv

        Notes:
            For xlsx files, it is assumed that the trading info is on the first sheet.

        Returns:
            The content of the file as a list of rows
        """

        if file.endswith('.xlsx'):
            # parse a excel sheet
            import xlrd

            # open the workbook
            wb = xlrd.open_workbook(file)

            # get the first sheet in the book
            sheet = wb.sheet_by_index(0)

            # convert cells to python types
            file_rows = [
                [c.value for c in row]
                for row in sheet.get_rows()
            ]

        elif file.endswith('.csv'):

            with open(file, 'r') as file_:

                file_rows = list(csv.reader(file_, **self._cfg))
        else:
            raise NotImplementedError(
                'The file format {} is currently not supported.'.format(os.path.splitext(file)[1]))

        if file_rows:

            result = []

            for row in file_rows:

                # a list for the new row with python datatypes
                row_ = []
                for col in row:

                    try:
                        row_.append(float(col))
                    except ValueError:

                        # try to parse as datetime
                        try:
                            row_.append(datetime.datetime.strptime(col, "%Y-%m-%d %H:%M:%S"))
                        except ValueError:
                            row_.append(col)

                # append the row to the result
                result.append(row_)

            return result

    def _write_transactions(self, transactions, file):
        """
        Write the transactions into the given file

        Args:
            transactions (list[dict]): A list of transaction entries as dicts.
            file: The file to write (either xl(s)x or csv

        Notes:
            For xlsx files, it is assumed that the trading info is on the first sheet.

        """
        if transactions:

            if file.endswith('.xlsx'):
                # parse a excel sheet
                import xlwt

                # create a new workbook
                wb = xlwt.Workbook()

                # and a sheet
                sheet = wb.add_sheet('sheet1')

                # write the header
                for c, head in enumerate(transactions[0].keys()):
                    sheet.write(0, c, head)

                # write all values
                for row, transaction in enumerate(transactions):
                    for col, value in enumerate(transaction.values()):
                        sheet.write(row + 1, col, value)

                wb.save(file)

            elif file.endswith('.csv'):

                with open(file, mode='w') as file_:

                    writer = csv.DictWriter(file_, fieldnames=transactions[0].keys(), **self._cfg)

                    writer.writerows(transactions)
            else:
                raise NotImplementedError(
                    'The file format {} is currently not supported.'.format(os.path.splitext(file)[1]))

    def __init__(self, **kwargs):

        super().__init__()

        self._cfg = kwargs
