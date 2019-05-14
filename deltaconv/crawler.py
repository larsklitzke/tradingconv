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
import datetime
import json
import logging
import sys

import requests


def parse_arguments():
    """Parses the arguments the user passed to this script """

    # parse parameter
    arg_parser = argparse.ArgumentParser(description="""
            BinanceCrawler can be used to retrieve detailed trading information of the cryptocurrency platform
            Binance without being restricted by the API provided by Binance. 
            
            This tool circumvent the trade history restriction of Binance, due to which only the trade history 
            for a three month interval can be exported.""")

    arg_parser.add_argument('--cookies', help='A file containing the cookies for a Binance session.', required=True)

    arg_parser.add_argument('--token', help='The csrftoken in the HTTP header.', required=True)

    arg_parser.add_argument('--output', help='The name of the CSV file with format.', required=True)

    arg_parser.add_argument('--start', help='The start datetime of the query interval in format YYYY-MM-DD HH:MM:SS',
                            required=True)

    arg_parser.add_argument('--end', help='The end datetime of the query interval. If not specified, the current date '
                                          'will be used', required=False, default=datetime.datetime.now())

    return arg_parser.parse_args()


class BinanceConnection(object):

    # Restricts the number of trades returned per request
    # We are currently sending multiple small requests
    # instead of one huge one to not stress Binance website.
    _MAX_TRADE_QUERY_COUNT = 1000

    def __init__(self, csrftoken, cookies):
        super().__init__()

        self._headers = {
            'origin': 'https://www.binance.com',
            'accept-encoding': 'gzip',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7',
            'lang': 'en',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36',
            'accept': '*/*',
            'cache-control': 'no-cache',
            'authority': 'www.binance.com',
            'dnt': '1',
            'clienttype': 'web',
            'csrftoken': '{}'.format(csrftoken),
        }

        self._cookies = {}

        # create a dict of the given cookie string
        cookie_list = cookies.split(';')

        for cookie in cookie_list:
            name, value = cookie.split('=')

            self._cookies[name] = value.strip()

    def _get_trades(self, start, end, symbol=None, type=None):
        """
        Retrieve the trades between `start` and `end`.

        Args:
            page (int|str):             The page number
            start (datetime.datetime):  The start date
            end (datetime.datetime):    Date of last transaction
            symbol (str):               The symbol to query, e.g. ETH, ADA, etc.
            type (str):                 The type of transaction; 'BUY' or 'SELL'

        Returns:
            tuple[int, dict]:           A tuple with the number of pages and the data of the specified page

        """

        logging.info('Get trades from %s to %s', start, end)

        post_data = {
            'start': int(start.timestamp()) * 1000,
            'end': int(end.timestamp()) * 1000,

            # take care of choosing this value - binance may reach out to you if you
            # set this value too high :P
            'rows': str(self._MAX_TRADE_QUERY_COUNT),

            'direction': '' if type is None else type,
            'baseAsset': '',
            'quoteAsset': '',
            'symbol': '' if symbol is None else symbol,
        }

        r = requests.post(
            url='https://www.binance.com/exchange/private/userTrades',
            headers=self._headers,
            allow_redirects=True,
            data=post_data,
            cookies=self._cookies
        )

        result = json.loads(r.text)

        return result['pages'], result['data']

    def trades(self, start, end, **kwargs):
        """
        Get all trades between `start` and `end`

        Args:
            start (datetime.datetime):   The start date
            end (datetime.datetime):     Date of last transaction
            **kwargs:
                symbol (str):   The symbol to query, e.g. ETH, ADA, etc.
                type (str):     The type of transaction; 'BUY' or 'SELL'

        Returns:
            list: A list of `Transaction`s

        """

        # since Binance only allows to retrieve three month in one query, we have to split up the request
        start_interval = start.replace(second=0, minute=0, hour=0, microsecond=0)

        # use 28 days to be save for all month
        end_interval = start_interval + datetime.timedelta(days=28)

        trades = []

        while end_interval < end:
            _, result = self._get_trades(start_interval, end_interval, **kwargs)

            trades.extend(result)

            start_interval = end_interval
            end_interval = start_interval + datetime.timedelta(days=28)

        # handle the last query since the interval should always overlap the full trading interval

        _, result = self._get_trades(start_interval, end, **kwargs)

        trades.extend(result)

        return trades


def main(arguments):
    # read in the cookies
    with open(arguments.cookies, 'r') as cookie_file:
        cookies = cookie_file.readlines()[0]

    conn = BinanceConnection(csrftoken=arguments.token, cookies=cookies)

    try:
        start_date = datetime.datetime.strptime(arguments.start, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('The given start time format is wrong. Format YYYY-MM-DD HH:MM:SS is required.')

    if not isinstance(arguments.end, datetime.datetime):
        try:
            end_date = datetime.datetime.strptime(arguments.end, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError('The given end time format is wrong. Format YYYY-MM-DD HH:MM:SS is required.')
    else:
        end_date = arguments.end

    trades = conn.trades(
        start=start_date,
        end=end_date,
    )

    # now write to the csv file
    with open(arguments.output, 'w') as csvfile:
        import csv

        writer = csv.writer(csvfile, delimiter=';')

        # use the keys of the first trade as csv file header
        writer.writerow(trades[0].keys())

        # just export all entries as rows
        for entry in trades:
            writer.writerow(entry.values())


if __name__ == '__main__':
    args = parse_arguments()

    formatter = logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    screenhandler = logging.StreamHandler(stream=sys.stdout)
    screenhandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(
        screenhandler
    )

    main(args)
