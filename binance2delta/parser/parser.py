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

    def __init__(self, **kwargs):

        super().__init__()

        self._cfg = kwargs
