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

from parser.binance import BinanceParser
from parser.delta import DeltaParser

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
