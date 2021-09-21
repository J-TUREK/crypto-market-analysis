# crypto-market-analysis
Analysing market trends and signals through statistical and technical indicators.

## Algorithm for finding optimal PNL from historic market close data using local maxima and minima points.
### Experimenting with varying maxima/ minima order.

```
main_optimal_trades_for_ohlc_data(df, subset_size=100, maxima_order=10, minima_order=5)

>> Number of trades: 2, Total return: 23.5552265177704%
>> Return / Trade ratio: 11.7776132588852 (Avg. return per trade)
```
![optimal_trade_algo_1](https://user-images.githubusercontent.com/69197760/134252138-5ac39563-22d4-4528-9e50-2d608a1032b3.png)

```
main_optimal_trades_for_ohlc_data(df, subset_size=100, maxima_order=2, minima_order=2)

>> Number of trades: 13, Total return: 35.012934865446056%
>> Return / Trade ratio: 2.693302681957389 (Avg. return per trade)
```
![optimal_trade_algo_2](https://user-images.githubusercontent.com/69197760/134252240-be44e952-6048-4929-b1d8-893e9d056cf8.png)

