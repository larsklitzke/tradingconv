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

import argparse

from binance2delta.parser.binance import BinanceParser, BinanceCrawlerParser
from binance2delta.parser.delta import DeltaParser

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
    },

    'binancecrawler': {
        'parser': BinanceCrawlerParser,
        'config': {
            'delimiter': ';',
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
