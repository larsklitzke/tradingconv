# tradingconv

Are you trading with Cryptocurrencies on [Binance](https://www.binance.com/)? Do you need a tool to manage the different file formats platforms 
like Binance uses for exporting the trading history, e.g. to import into tax return software or for tracking your 
portfolie in [delta](https://www.producthunt.com/posts/delta)? 

This package provide the appropriate tools for handling different formats of trading history files. Furthermore, the 
Binance API limitation that allows to only export trading history in an three month interval is lifted so that you can
export your **full** trading history. No need to generate an API key and expose it to third-party applications. Just 
use you local login session.

## Installation

This package is hosted on [PyPI](https://pypi.org/project/tradingconv/) so just install `tradingconv` with

```
pip install tradingconv
```

## Commands

This package comes equipped with multiple tools. Here is a list of currently available tools.

| Command          |  Description                                                 |
| -----------------| -------------------------------------------------------------|
| binancecrawler   | Query Binance to export the **full** trade history   |
| tradingconv      | Convert supported (csv,xlsx) files into other supported formats |



## Query Binance

Despite using the official API of Binance which limits the trade history to the last three month, 
`binancecrawler` is able to retrieve and export the **full** trade history.

Therefore, `binancecrawler` requires the session cookies of an active Binance connection on the current machine. 
The parameter `--cookies` should therefore point to a file containing a string with the cookies. 
)
### Save Binance session
In order to retrieve the Cookies of an active Binance session, log in into Binance and export the Cookies.
I've setup a list of links with a description on how to do this for different browser.

* [Chrome](https://developers.google.com/web/tools/chrome-devtools/manage-data/cookies)
* [Firefox](https://developer.mozilla.org/en-US/docs/Tools/Storage_Inspector#storage-tree)


![Warning](https://raw.githubusercontent.com/larsklitzke/binance2delta/master/doc/warning.png)

To the best of my knowledge, the following cookies are currently required in order to gain access to the active
session:

* JSESSIONID
* \_\_BINANCE_USER_DEVICE_ID\_\_

Save all of theses variables into a file with only one line in the following format:

```
line:=<var>+ <EOL>
var:=<variable>=<value>;
<variable> = "JSESSIONID" | "__BINANCE_USER_DEVICE_ID__ "
```

With ``<value>`` as the value of the variable. A line thus looks like:

```
JSESSIONID=<value>;__BINANCE_USER_DEVICE_ID__<value>
```

Finally, we need an additional csrftoken Binance uses for internal queries. You can read this token out by switching to 
your account page, open the development console of you browser (the one where you've copied the cookies from) and search
for an entry `getUserLoginLog.html`. You'll find the csrftoken in the header of the message.

![Image for retrieving the csrftoken](https://raw.githubusercontent.com/larsklitzke/binance2delta/master/doc/csrftoken_readout.jpg)

### Retrieve trade history

Now you can query Binance to retrieve your trade history within a specific inverval with

```
binancecrawler --cookies <cookie_file> --token <csrftoken> --start "2018-01-01 00:00:00" --end "2018-01-02 00:00:00" --output trade_file.csv
```

or simply the full history by passing a start some time ago your account creation. 

```
binancecrawler --cookies <cookie_file> --token <csrftoken> --start "2000-01-01 00:00:00" --output full_trade_file.csv
```

## Convert to other formats

To finally convert csv or xlxs files to the other csv or xlsx format, `tradingconv` does the trick.

The following source formats are supported:

* bitpanda: From the export function of the Bitpanda website
* binance: From the export function on the Binance website
* binancecrawler: The csv file created by `binancecrawler`

The following output formats are supported:

* binance: The xlsx format used by Binance.
* delta: The csv file format used by Delta.

More formats may supported in the future.

So, to convert the full trade history exported by `binancecrawler` to the delta format, simply call:

```
tradingconv --format delta --file full_trade_file.csv --output delta_trades.csv
```


## Thanks
If you like this tool, donate some bugs 💸 for a drink or two at the ETH-Wallet *0xbbf40ba9f8de33061ebd9eecafc0c4b2081ad14f*
or via [PayPal](https://www.paypal.me/LarsKlitzke). Cheers 🍻!

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

