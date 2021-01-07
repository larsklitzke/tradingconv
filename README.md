# tradingconv

Are you trading with Cryptocurrencies on [Binance](https://www.binance.com/)? Do you need a tool to manage the different file formats platforms 
like Binance uses for exporting the trading history, e.g. to import into tax return software or for tracking your 
portfolie in [delta](https://www.producthunt.com/posts/delta) or [CoinTracking](https://cointracking.info/)? 

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

| Command        | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| binancecrawler | Query Binance to export the **full** trade history              |
| tradingconv    | Convert supported (csv,xlsx) files into other supported formats |



## Query Binance

Despite using the official API of Binance which limits the trade history to the last three month, 
`binancecrawler` is able to retrieve and export the **full** trade history.

Therefore, `binancecrawler` requires the session cookies of an active Binance connection on the current machine. 
The parameter `--cookies` should therefore point to a file containing a string with the cookies. 

### Save Binance session
In order to retrieve the Cookies of an active Binance session, log in into Binance and export the Cookies.
I've setup a list of links with a description on how to do this for different browser.

* [Chrome](https://developers.google.com/web/tools/chrome-devtools/manage-data/cookies)
* [Firefox](https://developer.mozilla.org/en-US/docs/Tools/Storage_Inspector#storage-tree)


![Warning](https://raw.githubusercontent.com/larsklitzke/binance2delta/master/doc/warning.png)

To the best of my knowledge, the following cookies are currently required in order to gain access to the active
session:

* p20t

Save all of theses variables into a file with only one line in the following format:

```
line:=<var>+ <EOL>
var:=<variable>=<value>;
<variable> = "JSESSIONID" | "__BINANCE_USER_DEVICE_ID__ "
```

With ``<value>`` as the value of the variable. A line thus looks like:

```
p20t=<value>
```

Finally, we need an additional csrftoken Binance uses for internal queries. You can read this token out by switching to 
your account page, open the development console of you browser (the one where you've copied the cookies from) and search
for an entry `getUserLoginLog.html`. You'll find the `csrftoken` in the header of the message.

> Note that with the latest frontend update on Binance, the following image is outdated. Instead of searching for the 
> `getUserLoginLog.html` you can find the token in `get-open-orders` or any other request on the private Binance API.

![Image for retrieving the csrftoken](https://raw.githubusercontent.com/larsklitzke/binance2delta/master/doc/csrftoken_readout.jpg)

### Retrieve transaction history from binance

You can now use `binancecrawler` to get trades in a certain interval with

```bash
binancecrawler --cookies <cookie_file> \
               --token <csrftoken> \
               --start "2018-01-01 00:00:00"\
               --end "2018-01-02 00:00:00"\
               --output binance_trades.csv \
               --mode trade
```

or the full history by passing a start some time ago your account creation. 

```bash
binancecrawler --cookies <cookie_file> \
               --token <csrftoken> \
               --start "2018-01-01 00:00:00" \
               --output binance_trades.csv \
               --mode trading
```

For platforms such as [CoinTracking](https://cointracking.info/) you can also export all your deposits or withdrawals
from Binance by just changing the `mode`. For all deposits, run the following

```bash
binancecrawler --cookies <cookie_file> \
               --token <csrftoken> \
               --start "2018-01-01 00:00:00" \
               --output binance_deposits.csv \
               --mode deposit
```

and for all withdrawals

```bash
binancecrawler --cookies <cookie_file> \
               --token <csrftoken> \
               --start "2018-01-01 00:00:00" \
               --output binance_withdrawals.csv \
               --mode withdrawal
```
## Convert to other formats

To finally convert csv or xlxs files to the other csv or xlsx format, `tradingconv` does the trick.

The following source formats are supported:

* bitpanda: From the export function of the Bitpanda website
* binance: From the export function on the Binance website
* binancecrawler: The csv file(s) created by `binancecrawler`

The following output formats are supported:

* binance-trades: The xlsx format used by Binance for trades.
* binance-deposit: The xlsx format used by Binance for deposits.
* delta: The csv file format used by Delta.

More formats may supported in the future.

So, to convert the full trading history exported by `binancecrawler` to the delta format, simply call

```bash
tradingconv --format delta \
            --file binance_trades.csv \
            --output delta_trades.csv
```

or to the original binance format to import them into your portfolio tracking platform (e.g., CoinTracking) with

```bash
tradingconv --format binance \
            --file binance_trades.csv \
            --output binance_trades
```
The result is a `xlsx` with the same format as provided by Binance.

> Note that there is no need to specify the format of the source file. `tradingconv` will search for the correct parser 
> based on the columns in the file.

## Thanks
If you like this tools, donate some bugs 💸 for a drink or two via [PayPal](https://paypal.me/pools/c/8vQM2aoPHx). 
Cheers 🍻!

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

