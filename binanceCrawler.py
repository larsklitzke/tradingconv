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
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
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
import datetime
import json

import requests


def parse_arguments():
    '''Parses the arguments the user passed to this script '''

    # parse parameter
    arg_parser = argparse.ArgumentParser(description='''
            BinanceCrawler can be used to retrieve detailed trading information of the cryptocurrency ploatform
            Binance without being restricted by the API provided by Binance. 
            
            This tool circumvent the trade history restriction of Binance, due to which only the trade history 
            of the last three month can be exported.  
            ''')

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
    _MAX_TRADE_QUERY_COUNT = 20

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

    def _get_trade_page(self, page, start, end, symbol=None, type=None):

        post_data = {
            'start': int(start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()) * 1000,
            'end': int(end.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()) * 1000,
            'page': page,

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

        # get the first trade page
        pages, trades = self._get_trade_page(1, start, end, **kwargs)

        for page in range(2, pages + 1):
            _, result = self._get_trade_page(page, start, end, **kwargs)

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
        debug=True
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

    main(args)
