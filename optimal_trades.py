import numpy as np
from scipy.signal import argrelextrema
import pandas as pd
import math
import pytz
import time
import ast
import matplotlib.pyplot as plt


def optimal_return_minima_index(minima_subset, maxima_index, data):
    '''
    minima_subset = list of indexes of minima to try
    maxima = index of maxima to optimize
    data =  DataFrame to locate maxima and minima values at desired index
    '''
    largest_return = 0
    optimal_minima_index = None

    # For each minima point, get the minima which produces the largest return
    for i in minima_subset:
        buy_value = data.iloc[i]
        sell_value = data.iloc[maxima_index]
        trade_return = ((sell_value / buy_value) - 1) * 100

        if trade_return >= largest_return:
            largest_return = trade_return
            optimal_minima_index = i

    return optimal_minima_index, largest_return


def optimal_trades_for_ohlc_data(data: pd.DataFrame, subset_size=100, maxima_order=5, minima_order=5) -> list(dict()):

    data_subset = data.iloc[-subset_size:]

    closes_array = np.array(data_subset['close'].to_list())
    local_maxima = argrelextrema(closes_array, np.greater, order=maxima_order)
    local_minima = argrelextrema(closes_array, np.less, order=minima_order)

    local_maxima_indexes_list = local_maxima[0].tolist()
    local_minima_indexes_list = local_minima[0].tolist()

    trades = []

    for i in local_maxima_indexes_list:
        minima_subset = list(
            filter(lambda x: x < i, local_minima_indexes_list))
        if minima_subset == []:
            continue

        optimal_minima_index, optimal_return = optimal_return_minima_index(
            minima_subset, i, data_subset['close'])

        try:
            trades.append({
                "buy_index": optimal_minima_index,
                "buy_price": data_subset['close'].iloc[optimal_minima_index],
                "sell_index": i,
                "sell_price": data_subset['close'].iloc[i],
                "return": optimal_return
            })
        except Exception as ex:
            print(ex)
            print(optimal_minima_index)
            print(minima_subset)
            continue

        local_minima_indexes_list = list(
            set(local_minima_indexes_list) - set(minima_subset))

    return trades


def cummulative_trades_return(trade_data):
    '''
    Accepts array of the form:
    [
    {
        "buy_index" : int,
        "buy_price" : float,
        "sell_index" : int,
        "sell_price" : float,
        "return": float
    },
    ]
    '''
    total_return = 0
    for trade in trade_data:
        total_return += trade['return']

    return total_return


def main_optimal_trades_for_ohlc_data(data: pd.DataFrame, subset_size=100, maxima_order=10, minima_order=5, print_trades=False):

    trades = optimal_trades_for_ohlc_data(
        data, subset_size=subset_size, maxima_order=maxima_order, minima_order=minima_order)
    total_return = cummulative_trades_return(trades)

    data_subset = data.iloc[-subset_size:]

    ax = data.iloc[-subset_size:]['close'].plot(figsize=(15, 8))

    buy_label = "buy"
    sell_label = "sell"

    for trade in trades:
        x_buy = data_subset.index[trade['buy_index']]
        y_buy = trade['buy_price']

        x_sell = data_subset.index[trade['sell_index']]
        y_sell = trade['sell_price']

        ax.text(x_buy, y_buy, buy_label)
        ax.text(x_sell, y_sell, sell_label)

    if print_trades:
        print(trades)

    print(f"Number of trades: {len(trades)}, Total return: {total_return}%")
    print(
        f"Return / Trade ratio: {total_return / len(trades)} (Avg. return per trade)")

    return trades
