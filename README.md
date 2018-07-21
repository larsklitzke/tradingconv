# binance2delta

This package contains tools to retrieve information of the cryptocurrency exchange [Binance](https://www.binance.com/)
to generate .csv files which can be imported into the trading application [delta](https://www.producthunt.com/posts/delta). 
No need to generate an API key and expose it to third-party applications. Supports export of the 
**full** trading history.

## Installation

This package is hosted on [PyPI](https://pypi.org/project/binance2delta/) so just install `binance2delta` with

```
pip install binance2delta
```

## Comands

This package comes equipped with multiple tools. Here is a list of currently available tools.

| Command          |  Description                                                 |
| -----------------| -------------------------------------------------------------|
| binancecrawler   | Query Binance to export the **full** trade history   |
| binance2delta    | Convert supported (csv,xlsx) files into the delta csv format |



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

<aside class="warning">
Do not expose the Cookies to the public and remove the files afterwards!
</aside>


To the best of my knowledge, the following cookies are currently required in order to gain access to the active
session:

* _ga
* sensorsdata2015jssdkcross
* JSESSIONID
* \_\_BINANCE_USER_DEVICE_ID\_\_

Save all of theses variables into a file with only one line in the following format:

```
line:=<var>+ <EOL>
var:=<variable>=<value>;
<variable> = "_ga" | "JSESSIONID" | "__BINANCE_USER_DEVICE_ID__ "
```

With ``<value>`` as the value of the variable. A line thus looks like:

```
_ga=<value>;JSESSIONID=<value>;__BINANCE_USER_DEVICE_ID__<value>
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

## Convert to delta format

To finally convert csv or xlxs files created either using Binance export function or 
`binancecrawler` to the delta csv format, `binance2delta` does the trick.

Currently, the following source formatter are supported:

* binance: By using the export function on the Binance website
* binancecrawler: The csv file created by `binancecrawler`

More formats may supported in the future.


So, to convert the full trade history exported by `binancecrawler` simply call:

```
binance2delta --format binancecrawler --file full_trade_file.csv --output delta_trades.csv
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

