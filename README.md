# binance2delta

Python tool to convert binance transaction .csv files to the csv file format supported by [delta](https://www.producthunt.com/posts/delta)

To convert a csv file in the binance format, simply run binance2delta as following:

```
binance2delta --format binance --file binance_trades.(csv|xlsx) --output delta_trades.csv
```

