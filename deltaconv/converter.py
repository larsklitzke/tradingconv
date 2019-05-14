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
import logging
import sys

from deltaconv.parser.binance import BinanceParser, BinanceCrawlerParser
from deltaconv.parser.bitpanda import BitpandaParser
from deltaconv.parser.delta import DeltaParser
from deltaconv.parser.parser import ParserOutdatedError

PARSER = {
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
    },

    'bitpanda': {
        'parser': BitpandaParser,
        'config': {
            'delimiter': ','
        }
    }
}

# The list of available csv file exporter
EXPORTER = {name: PARSER[name] for name in ['binance', 'delta']}


def parse_arguments():
    """Parses the arguments the user passed to this script """

    # parse parameter
    arg_parser = argparse.ArgumentParser(description='''
            This tool parses a range of CSV|XLSX files into other CSV|XLSX file formats, e.g. Delta, Bitpanda or 
            Binance.''')

    arg_parser.add_argument('--file', help="The csv file", required=True)

    arg_parser.add_argument('--format', help="The output transaction format.", required=True, choices=PARSER.keys())

    arg_parser.add_argument('--output', help="The name of the file to save the transactions into without extension.",
                            required=False, default=None)

    return arg_parser.parse_args()


def init_parser(source_format):
    """ Initialize a Parser based on the given source format

    Args:
        source_format: The format of the source file, e.g. binance.
    """

    choice = PARSER[source_format]

    return choice['parser'](**choice['config'])


if __name__ == "__main__":
    arguments = parse_arguments()

    formatter = logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    screenhandler = logging.StreamHandler(stream=sys.stdout)
    screenhandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(
        screenhandler
    )

    transaction_list = []
    parser = None

    logging.info('Try to parse the file %s', arguments.file)
    for name in PARSER:
        try:
            parser = init_parser(name)

            transaction_list = parser.parse(arguments.file)

            break
        except (ParserOutdatedError, NotImplementedError):
            pass

    if not transaction_list:
        logging.error('The format of the given file is currently not supported.')

    else:
        logging.info('Parsing was successful.')
        logging.info('Export %d transactions to %s.', len(transaction_list), arguments.output)
        parser = init_parser(arguments.format)

        parser.export(transaction_list, arguments.output)

        logging.info('Finished - will exit gracefully.')
